import pytest
from cleanedweb.models import CatalogApi, EndpointContract

from tools.common import (
    InputError,
    describe_endpoint,
    json_object,
    positive_int,
    rank,
    split_list,
)


def api(api_id, name, key_fields=(), domain="example.com"):
    return CatalogApi.from_dict(
        {"api_id": api_id, "name": name, "key_fields": list(key_fields), "site": {"domain": domain}}
    )


def test_rank_by_words_then_fields():
    apis = [
        api("a", "Used Cars"),
        api("b", "GitHub Topic Repositories", ["title"]),
        api("c", "GitHub Repository Search", ["title", "stargazer_count"]),
    ]
    assert [a.api_id for a in rank(apis, "github repositories", ["stargazer_count"])] == ["c", "b"]
    assert [a.api_id for a in rank(apis, "", [])] == ["a", "b", "c"]
    assert rank(apis, "zzqx", []) == []


def test_inputs_are_checked_before_any_request():
    assert json_object('{"search": "rails"}', "input") == {"search": "rails"}
    assert json_object("", "input") == {}
    with pytest.raises(InputError):
        json_object("[1]", "input")
    with pytest.raises(InputError):
        json_object("{bad", "input")
    assert positive_int(None, "max_items", 20) == 20
    assert positive_int("70", "limit", 10, 50) == 50
    with pytest.raises(InputError):
        positive_int("0", "max_items", 20)
    assert split_list(" title, price ,,") == ["title", "price"]


def test_describe_endpoint_lists_inputs_outputs_and_short_samples():
    endpoint = EndpointContract.from_dict(
        {
            "endpoint_id": "e",
            "input_schema": {
                "properties": {"search": {"anyOf": [{"type": "string"}, {"type": "array"}], "default": "rails"}},
                "required": [],
            },
            "output_schema": {"properties": {"title": {"type": "string"}}, "required": ["title"]},
            "examples": [{"records": [{"title": "x" * 400}] * 5}],
        }
    )
    described = describe_endpoint(endpoint)
    assert described["inputs"] == [{"name": "search", "type": "string or array", "required": False, "default": "rails"}]
    assert described["output_fields"] == [{"name": "title", "type": "string", "required": True}]
    assert len(described["sample_records"]) == 3
    assert described["sample_records"][0]["title"].endswith("…")
