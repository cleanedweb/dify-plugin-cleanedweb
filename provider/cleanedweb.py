from typing import Any

from cleanedweb.exceptions import CleanedWebError
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.common import client_for


class CleanedWebProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        if not str(credentials.get("api_key") or "").strip():
            raise ToolProviderCredentialValidationError("Enter a CleanedWeb API key.")
        # Listing the newest run needs the key and never starts a run or uses credit.
        try:
            with client_for(credentials) as cw:
                cw.runs.list(limit=1)
        except CleanedWebError as exc:
            raise ToolProviderCredentialValidationError(f"CleanedWeb did not accept the key: {exc}") from None
