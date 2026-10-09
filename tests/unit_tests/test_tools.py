import asyncio
import json
from unittest.mock import patch

import httpx
import pytest
from langchain_core.messages import ToolMessage
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import ValidationError

from langchain_flashdata import (
    FlashDataError,
    FlashDataGoogleSearch,
    FlashDataToolkit,
    FlashDataYouTubeMetadata,
    FlashDataYouTubeSearch,
    FlashDataYouTubeTranscript,
)
from langchain_flashdata._client import QUERY_URL

CASES = [
    (
        FlashDataGoogleSearch,
        {"query": "  LangChain  ", "num": 3, "autocorrect": False},
        {
            "source": "google_search",
            "query": "LangChain",
            "params": {"num": 3, "page": 1, "autocorrect": False},
        },
    ),
    (
        FlashDataYouTubeSearch,
        {"query": "LangGraph", "max_results": 2},
        {"source": "youtube_search", "query": "LangGraph", "params": {"max_results": 2}},
    ),
    (
        FlashDataYouTubeMetadata,
        {"video_id": "https://youtu.be/dQw4w9WgXcQ", "include_formats": False},
        {
            "source": "youtube_metadata",
            "video_id": "dQw4w9WgXcQ",
            "params": {"include_chapters": True, "include_formats": False},
        },
    ),
    (
        FlashDataYouTubeTranscript,
        {"video_id": "dQw4w9WgXcQ", "auto": False},
        {
            "source": "youtube_transcript",
            "video_id": "dQw4w9WgXcQ",
            "params": {"language": "en", "auto": False},
        },
    ),
]


@pytest.mark.parametrize("tool_type,arguments,payload", CASES)
@pytest.mark.parametrize("async_mode", [False, True])
def test_request_contract_and_result(mock_api, tool_type, arguments, payload, async_mode):
    requests = []
    # Some successful API responses omit status; preserve the full envelope.
    expected = {
        "source": payload["source"],
        "results": [{"title": "A result"}],
        "usage": {"credits": 0.004},
        "created_at": "2026-10-09T00:00:00Z",
    }

    def handler(request):
        requests.append(request)
        assert str(request.url) == QUERY_URL
        assert request.method == "POST"
        assert request.headers["X-API-Key"] == "test-secret"
        assert request.headers["X-Request-Id"]
        assert "authorization" not in request.headers
        assert json.loads(request.content) == payload
        return httpx.Response(200, json=expected)

    sync_patch, async_patch = mock_api(handler)
    with sync_patch, async_patch:
        tool = tool_type(api_key="test-secret")
        result = asyncio.run(tool.ainvoke(arguments)) if async_mode else tool.invoke(arguments)
    assert result == expected
    assert len(requests) == 1


@pytest.mark.parametrize("status", [301, 401, 402, 403, 429, 500, 503])
@pytest.mark.parametrize("async_mode", [False, True])
def test_errors_never_retry_redirect_or_echo_body(mock_api, status, async_mode):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status,
            text="raw-private-upstream-body",
            headers={"Location": "https://example.org/collect"},
        )

    sync_patch, async_patch = mock_api(handler)
    with sync_patch, async_patch, pytest.raises(FlashDataError) as error:
        tool = FlashDataGoogleSearch(api_key="test-secret")
        if async_mode:
            asyncio.run(tool.ainvoke({"query": "test"}))
        else:
            tool.invoke({"query": "test"})
    assert str(status) in str(error.value)
    assert "test-secret" not in str(error.value)
    assert "raw-private" not in str(error.value)
    assert len(requests) == 1


@pytest.mark.parametrize("async_mode", [False, True])
def test_timeout_has_unknown_outcome_and_one_submission(mock_api, async_mode):
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("private upstream details", request=request)

    sync_patch, async_patch = mock_api(handler)
    with sync_patch, async_patch, pytest.raises(FlashDataError, match="may already be charged"):
        tool = FlashDataGoogleSearch(api_key="test-secret")
        if async_mode:
            asyncio.run(tool.ainvoke({"query": "test"}))
        else:
            tool.invoke({"query": "test"})
    assert len(calls) == 1


@pytest.mark.parametrize(
    "body",
    [
        [],
        {},
        {"results": {}},
        {"status": "running", "results": []},
        {"status": "failed", "results": []},
        {"job": {"status": "failed"}, "results": []},
    ],
)
def test_incomplete_response_is_not_success(mock_api, body):
    sync_patch, _ = mock_api(lambda request: httpx.Response(200, json=body))
    with sync_patch, pytest.raises(FlashDataError, match="Jobs"):
        FlashDataGoogleSearch(api_key="test-secret").invoke({"query": "test"})


def test_invalid_json_is_unknown_outcome(mock_api):
    sync_patch, _ = mock_api(lambda request: httpx.Response(200, text="not JSON"))
    with sync_patch, pytest.raises(FlashDataError, match="may already be charged"):
        FlashDataGoogleSearch(api_key="test-secret").invoke({"query": "test"})


@pytest.mark.parametrize(
    "tool_type,arguments",
    [
        (FlashDataGoogleSearch, {"query": " "}),
        (FlashDataGoogleSearch, {"query": "x" * 2001}),
        (FlashDataGoogleSearch, {"query": "test", "num": True}),
        (FlashDataGoogleSearch, {"query": "test", "num": 101}),
        (FlashDataGoogleSearch, {"query": "test", "page": 0}),
        (FlashDataGoogleSearch, {"query": "test", "gl": "USA"}),
        (FlashDataGoogleSearch, {"query": "test", "autocorrect": "false"}),
        (FlashDataGoogleSearch, {"query": "test", "unexpected": 1}),
        (FlashDataYouTubeSearch, {"query": "test", "max_results": 21}),
        (FlashDataYouTubeTranscript, {"video_id": "dQw4w9WgXcQ", "language": "en/US"}),
        (
            FlashDataYouTubeTranscript,
            {"video_id": "https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ"},
        ),
        (
            FlashDataYouTubeMetadata,
            {"video_id": "https://user:pass@youtube.com/watch?v=dQw4w9WgXcQ"},
        ),
        (FlashDataYouTubeMetadata, {"video_id": "https://youtu.be/dQw4w9WgXcQ/extra"}),
        (FlashDataYouTubeMetadata, {"video_id": "http://[invalid"}),
    ],
)
def test_invalid_input_never_submits(tool_type, arguments):
    with patch("langchain_flashdata._client.query") as query, pytest.raises(ValidationError):
        tool_type(api_key="test-secret").invoke(arguments)
    query.assert_not_called()


@pytest.mark.parametrize("status", ["done", "completed"])
def test_tool_call_yields_tool_message(mock_api, status):
    body = {"status": status, "results": [], "usage": {"credits": 0}}
    sync_patch, _ = mock_api(lambda request: httpx.Response(200, json=body))
    with sync_patch:
        result = FlashDataGoogleSearch(api_key="test-secret").invoke(
            {
                "name": "flashdata_google_search",
                "args": {"query": "test"},
                "id": "call_1",
                "type": "tool_call",
            }
        )
    assert isinstance(result, ToolMessage)
    assert result.tool_call_id == "call_1"
    assert json.loads(result.content) == body


def test_toolkit_schemas_and_serialization_hide_secrets(monkeypatch):
    monkeypatch.setenv("FLASHDATA_API_KEY", "test-secret")
    toolkit = FlashDataToolkit()
    tools = toolkit.get_tools()
    assert len({tool.name for tool in tools}) == 4
    for obj in [toolkit, *tools]:
        assert "test-secret" not in repr(obj)
        assert "test-secret" not in str(obj.model_dump())
    for tool in tools:
        assert "test-secret" not in str(tool.to_json())
        schema = convert_to_openai_tool(tool)
        assert "api_key" not in str(schema)
        assert schema["function"]["parameters"]["properties"]


def test_missing_and_empty_credentials(monkeypatch):
    monkeypatch.delenv("FLASHDATA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="FLASHDATA_API_KEY"):
        FlashDataGoogleSearch()
    with pytest.raises(ValueError, match="must not be empty"):
        FlashDataGoogleSearch(api_key=" ")
