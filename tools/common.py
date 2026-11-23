"""Shared helpers for the CleanedWeb tools. No Tool subclass lives here: Dify loads the one in each tool file."""

from __future__ import annotations

import json
import re
from typing import Any

from cleanedweb import CleanedWeb
from cleanedweb.models import ApiContract, CatalogApi, EndpointContract

SITE_URL = "https://cleanedweb.com"
HTTP_TIMEOUT_SECONDS = 30.0
SAMPLE_RECORDS = 3
SAMPLE_TEXT_CHARS = 300
INPUT_EXAMPLES = 10
STOP_WORDS = frozenset(
    ["a", "an", "and", "api", "apis", "by", "data", "for", "from", "in", "list", "of", "on", "the", "to", "with"]
)


class InputError(ValueError):
    """The tool input cannot become a request; nothing was sent or charged."""


def client_for(credentials: dict[str, Any] | None) -> CleanedWeb:
    api_key = str((credentials or {}).get("api_key") or "").strip() or None
    return CleanedWeb(api_key=api_key, timeout=HTTP_TIMEOUT_SECONDS)


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def compact(value: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in value.items() if v is not None and v != [] and v != ""}


def split_list(value: Any) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        items = text(value).split(",")
    return [str(item).strip() for item in items if str(item).strip()]


def json_object(value: Any, name: str) -> dict[str, Any]:
    if value is None or (isinstance(value, str) and not value.strip()):
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        raise InputError(f"'{name}' must be a JSON object, such as {{\"search\": \"rails\"}}.") from None
    if not isinstance(parsed, dict):
        raise InputError(f"'{name}' must be a JSON object, such as {{\"search\": \"rails\"}}.")
    return parsed


def positive_int(value: Any, name: str, default: int, maximum: int | None = None) -> int:
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        raise InputError(f"'{name}' must be a whole number.") from None
    if number < 1:
        raise InputError(f"'{name}' must be 1 or more.")
    return min(number, maximum) if maximum else number


def words(value: str) -> list[str]:
    return [w for w in re.split(r"[^a-z0-9]+", value.lower()) if len(w) > 1 and w not in STOP_WORDS]


def stem(word: str) -> str:
    """Word stems: `repositories` and `repository` meet at `repositor`."""
    return re.sub(r"(ies|es|s|y)$", "", word)


def haystack(api: CatalogApi) -> set[str]:
    raw = api.raw or {}
    parts: list[Any] = [api.name, api.description, api.site_name, api.site_domain, api.category]
    parts += api.key_fields
    parts += raw.get("tags") or []
    parts += raw.get("record_types") or []
    parts += [endpoint.name for endpoint in api.endpoints]
    return {stem(w) for w in words(" ".join(str(p) for p in parts if p))}


def rank(apis: list[CatalogApi], query: str, fields: list[str]) -> list[CatalogApi]:
    query_words = list(dict.fromkeys(stem(w) for w in words(query)))
    wanted = [f.lower() for f in fields]
    scored = []
    for order, api in enumerate(apis):
        hay = haystack(api)
        key_fields = {f.lower() for f in api.key_fields}
        word_hits = sum(1 for w in query_words if w in hay)
        if query_words and word_hits == 0:
            continue
        field_hits = sum(1 for f in wanted if f in key_fields)
        scored.append((-word_hits, -field_hits, order, api))
    scored.sort(key=lambda entry: entry[:3])
    return [entry[3] for entry in scored]


def summarize_api(api: CatalogApi, fields: list[str]) -> dict[str, Any]:
    key_fields = {f.lower() for f in api.key_fields}
    wanted = [f.lower() for f in fields]
    return compact(
        {
            "api_id": api.api_id,
            "slug": api.slug,
            "name": api.name,
            "description": api.description,
            "site": api.site_domain,
            "category": api.category,
            "health": api.health,
            "key_fields": api.key_fields,
            "fields_matched": [f for f in wanted if f in key_fields] if wanted else None,
            "fields_missing": [f for f in wanted if f not in key_fields] if wanted else None,
            "page_url": f"{SITE_URL}/catalog/{api.slug}/?utm_source=dify&utm_medium=plugin" if api.slug else None,
            "endpoints": [
                compact({"endpoint_id": e.endpoint_id, "name": e.name, "description": e.description})
                for e in api.endpoints
            ],
        }
    )


def shorten(value: Any) -> Any:
    if isinstance(value, str):
        return value[:SAMPLE_TEXT_CHARS] + "…" if len(value) > SAMPLE_TEXT_CHARS else value
    if isinstance(value, list):
        return [shorten(v) for v in value]
    if isinstance(value, dict):
        return {k: shorten(v) for k, v in value.items()}
    return value


def schema_type(schema: dict[str, Any]) -> str | None:
    if isinstance(schema.get("type"), str):
        return schema["type"]
    variants = [s.get("type") for s in schema.get("anyOf") or [] if isinstance(s, dict)]
    names = [v for v in variants if isinstance(v, str)]
    return " or ".join(dict.fromkeys(names)) or None


def describe_endpoint(endpoint: EndpointContract) -> dict[str, Any]:
    input_schema = endpoint.input_schema or {}
    properties = input_schema.get("properties") or {}
    required = set(input_schema.get("required") or [])
    inputs = []
    for name, schema in properties.items():
        schema = schema if isinstance(schema, dict) else {}
        inputs.append(
            compact(
                {
                    "name": name,
                    "type": schema_type(schema),
                    "required": name in required,
                    "default": schema.get("default"),
                    "description": schema.get("description"),
                    "allowed": schema.get("enum"),
                    "examples": (schema.get("examples") or [])[:INPUT_EXAMPLES] or None,
                }
            )
        )
    output_schema = endpoint.output_schema or {}
    output_required = set(output_schema.get("required") or [])
    output_fields = [
        compact({"name": name, "type": schema_type(s if isinstance(s, dict) else {}), "required": name in output_required})
        for name, s in (output_schema.get("properties") or {}).items()
    ]
    samples: list[Any] = []
    for example in endpoint.examples or []:
        if isinstance(example, dict):
            samples += [r for r in example.get("records") or [] if isinstance(r, dict)]
    return compact(
        {
            "endpoint_id": endpoint.endpoint_id,
            "name": endpoint.name,
            "description": endpoint.description,
            "inputs": inputs,
            "output_fields": output_fields,
            "sample_records": [shorten(r) for r in samples[:SAMPLE_RECORDS]],
        }
    )


def describe_api(contract: ApiContract, endpoint_id: str) -> dict[str, Any]:
    endpoints = [e for e in contract.endpoints if not endpoint_id or e.endpoint_id == endpoint_id]
    if endpoint_id and not endpoints:
        known = ", ".join(e.endpoint_id for e in contract.endpoints)
        raise InputError(f"API {contract.api_id} has no endpoint {endpoint_id}. Its endpoints: {known}.")
    return compact(
        {
            "api_id": contract.api_id,
            "name": contract.name,
            "description": contract.description,
            "site": contract.site_domain,
            "limitations": contract.limitations,
            "endpoints": [describe_endpoint(e) for e in endpoints],
            "note": "sample_records were saved when the API was accepted; they are not a live run.",
        }
    )
