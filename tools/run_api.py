from collections.abc import Generator
from typing import Any

from cleanedweb.exceptions import CleanedWebError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import (
    InputError,
    client_for,
    compact,
    json_object,
    positive_int,
    split_list,
    text,
)

# Dify ends a tool call after 120 seconds; stop waiting before that and hand back the key.
POLL_TIMEOUT_SECONDS = 90.0
USABLE_STATUSES = ("completed", "bounded")


class RunApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api_id = text(tool_parameters.get("api_id"))
            endpoint_id = text(tool_parameters.get("endpoint_id"))
            if not api_id or not endpoint_id:
                raise InputError("Give the api_id and endpoint_id that find_api returned.")
            run_input = json_object(tool_parameters.get("input"), "input")
            max_items = positive_int(tool_parameters.get("max_items"), "max_items", 20)
            fields = split_list(tool_parameters.get("fields")) or None
            key = text(tool_parameters.get("idempotency_key")) or None
            with client_for(self.runtime.credentials) as cw:
                result = cw.catalog.run(
                    api_id,
                    endpoint_id,
                    run_input,
                    max_items=max_items,
                    fields=fields,
                    idempotency_key=key,
                    poll_timeout=POLL_TIMEOUT_SECONDS,
                )
        except InputError as exc:
            yield self.create_text_message(f"Invalid input: {exc} Nothing was charged.")
            return
        except CleanedWebError as exc:
            yield self.create_text_message(f"CleanedWeb error: {exc}")
            return
        run = result.run or {}
        summary = result.summary or {}
        if not result.complete:
            yield self.create_json_message(
                compact(
                    {
                        "finished": False,
                        "run_id": run.get("run_id"),
                        "idempotency_key": result.idempotency_key,
                        "records_so_far": len(result.records),
                        "note": "The run is still going. Call run_api again with the same api_id, endpoint_id, "
                        "input and this idempotency_key to wait for it; it is not run or charged twice.",
                    }
                )
            )
            return
        problems = []
        if summary.get("status") not in USABLE_STATUSES:
            problems.append(f"summary.status is {summary.get('status')!r}")
        if summary.get("within_scope_passed") is not True:
            problems.append("within_scope_passed is not true")
        if run.get("status", "finished") != "finished":
            problems.append(f"run.status is {run.get('status')!r}")
        output = compact(
            {
                "finished": True,
                "accepted": result.is_usable,
                "problems": problems or None,
                "record_count": len(result.records),
                "status": summary.get("status"),
                "stop_reason": run.get("stop_reason"),
                "units_charged": run.get("units_charged"),
                "run_id": run.get("run_id"),
                "idempotency_key": result.idempotency_key,
                "version": result.version,
            }
        )
        output["records"] = result.records
        yield self.create_json_message(output)
