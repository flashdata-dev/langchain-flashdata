import json

import httpx
import pytest
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, ToolMessage

from langchain_flashdata import FlashDataError, FlashDataGoogleSearch


class ScriptedModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def call_message(*ids):
    return AIMessage(
        content="",
        tool_calls=[
            {"id": value, "name": "flashdata_google_search", "args": {"query": "LangChain"}}
            for value in ids
        ],
    )


def make_agent(messages, limit=2):
    return create_agent(
        ScriptedModel(responses=messages),
        tools=[FlashDataGoogleSearch(api_key="test-secret")],
        middleware=[ToolCallLimitMiddleware(run_limit=limit, exit_behavior="error")],
    )


def test_langgraph_agent_receives_real_tool_output(mock_api):
    body = {"results": [{"organic": [{"link": "https://docs.langchain.com"}]}]}
    sync_patch, _ = mock_api(lambda request: httpx.Response(200, json=body))
    with sync_patch:
        result = make_agent([call_message("call_1"), AIMessage(content="Done")]).invoke(
            {"messages": [{"role": "user", "content": "Research LangChain"}]}
        )
    tool_message = next(msg for msg in result["messages"] if isinstance(msg, ToolMessage))
    assert json.loads(tool_message.content) == body
    assert result["messages"][-1].content == "Done"


def test_agent_stops_on_unknown_query_outcome(mock_api):
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout("connection lost", request=request)

    sync_patch, _ = mock_api(handler)
    with sync_patch, pytest.raises(FlashDataError, match="may already be charged"):
        make_agent([call_message("call_1"), call_message("call_2")]).invoke(
            {"messages": [{"role": "user", "content": "Research LangChain"}]}
        )
    assert len(calls) == 1


def test_agent_budget_blocks_excess_calls_before_submission(mock_api):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"results": []})

    sync_patch, _ = mock_api(handler)
    with sync_patch, pytest.raises(ToolCallLimitExceededError):
        make_agent([call_message("call_1", "call_2")], limit=1).invoke(
            {"messages": [{"role": "user", "content": "Research LangChain"}]}
        )
    assert calls == []
