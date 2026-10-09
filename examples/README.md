# Runnable examples

Install from the repository with `pip install '.[examples]'` and set
`FLASHDATA_API_KEY`. No example contains a real key. Direct calls consume
FlashData credits; research examples also use your model provider account.

## Direct calls without a model

Each command makes one asynchronous API query:

```bash
python examples/direct_tools.py google_search '{"query":"LangChain tools","num":3}'
python examples/direct_tools.py youtube_search '{"query":"LangGraph tutorial","max_results":2}'
python examples/direct_tools.py youtube_metadata '{"video_id":"dQw4w9WgXcQ","include_formats":false}'
python examples/direct_tools.py youtube_transcript '{"video_id":"dQw4w9WgXcQ","language":"en","auto":false}'
```

## Research with an agent

Set `OPENAI_API_KEY` and `OPENAI_MODEL` for a tool-calling model. Set
`OPENAI_BASE_URL` only if using a Chat Completions compatible gateway.

```bash
python examples/research_agent.py \
  'Search Google for LangGraph tutorials. Request 3 results. Summarize them and cite URLs.' \
  --max-tool-calls 1

python examples/research_agent.py \
  'Retrieve the manual English transcript of https://youtu.be/dQw4w9WgXcQ. Describe the main themes and cite available timestamps.' \
  --max-tool-calls 1
```

The model chooses the tool and input. There is no fixed search or summarization
pipeline. `create_agent` runs on LangGraph, and `ToolCallLimitMiddleware` blocks
tool calls above the selected run budget. The package and examples do not retry
queries after transport failures. An error stops the run; inspect the FlashData
Jobs page before deciding to submit again.

## Connect your existing hosted MCP

```bash
pip install '.[mcp]'
python examples/hosted_mcp.py
```

This discovers tool names only, without submitting a paid query. It uses
`MCPAdapter` from `langchain.mcp` (LangChain >=1.4, beta), with a
`StreamableHttpTransport` carrying the `X-API-Key` header. You do not need to
start a local MCP server or install FlashData's stdio npm package.

To use MCP with an agent, pass only the desired tools returned by
`adapter.list_tools()` to `create_agent`. Review their descriptions and scopes;
the MCP catalog includes paid queries as well as free account/job reads. Apply
your own query budget and stop on unknown outcomes. The discovery example does
not exercise every MCP tool.
