from collections.abc import Generator
from typing import Any

from cleanedweb.exceptions import CleanedWebError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import (
    InputError,
    client_for,
    positive_int,
    rank,
    split_list,
    summarize_api,
    text,
)


class FindApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            query = text(tool_parameters.get("query"))
            site = text(tool_parameters.get("site"))
            category = text(tool_parameters.get("category"))
            fields = split_list(tool_parameters.get("fields"))
            limit = positive_int(tool_parameters.get("limit"), "limit", 10, 50)
            with client_for(self.runtime.credentials) as cw:
                apis = cw.catalog.find(site=site or None, category=category or None, limit=10_000)
        except InputError as exc:
            yield self.create_text_message(f"Invalid input: {exc} Nothing was charged.")
            return
        except CleanedWebError as exc:
            yield self.create_text_message(f"CleanedWeb error: {exc}")
            return
        ranked = rank(apis, query, fields)
        output: dict[str, Any] = {"total": len(ranked), "apis": [summarize_api(a, fields) for a in ranked[:limit]]}
        if not ranked:
            output["note"] = (
                "No published API covers that site or category. Search without them to see what the catalog has."
                if not apis
                else "No API matched those words. Try fewer or broader words, or search by site alone."
            )
        yield self.create_json_message(output)
