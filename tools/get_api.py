from collections.abc import Generator
from typing import Any

from cleanedweb.exceptions import CleanedWebError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.common import InputError, client_for, describe_api, text


class GetApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            api_id = text(tool_parameters.get("api_id"))
            if not api_id:
                raise InputError("Give the api_id or slug that find_api returned.")
            with client_for(self.runtime.credentials) as cw:
                contract = cw.catalog.get(api_id)
            output = describe_api(contract, text(tool_parameters.get("endpoint_id")))
        except InputError as exc:
            yield self.create_text_message(f"Invalid input: {exc} Nothing was charged.")
            return
        except CleanedWebError as exc:
            yield self.create_text_message(f"CleanedWeb error: {exc}")
            return
        yield self.create_json_message(output)
