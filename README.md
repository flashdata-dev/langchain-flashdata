# langchain-flashdata

[FlashData](https://flashdata.dev) tools for Google Search, YouTube video search,
video metadata, and transcripts. Give LangChain and LangGraph agents current web
and video data with source URLs and timestamped captions.

This package is maintained by FlashData. It implements LangChain's `BaseTool` and
`BaseToolkit` interfaces with synchronous and native asynchronous HTTP calls.

## Installation

Requires Python 3.10 or newer (below Python 4). Install from
[PyPI](https://pypi.org/project/langchain-flashdata/):

```bash
pip install -U langchain-flashdata
```

Create an API key in the [FlashData console](https://flashdata.dev), enable the
sources you need, and provide it through your environment:

```bash
export FLASHDATA_API_KEY='YOUR_FLASHDATA_API_KEY'
```

Queries consume FlashData credits. Check [current pricing](https://flashdata.dev/pricing)
and your account's available credits before running examples. Model provider
charges are separate.

## Quick start

```python
from langchain_flashdata import FlashDataGoogleSearch

search = FlashDataGoogleSearch()
result = search.invoke({"query": "LangGraph durable execution", "num": 3})
for item in result["results"][0].get("organic", []):
    print(item.get("title"), item.get("link"))
```

All tools also accept `api_key="..."` at construction time. Do not put real keys
in source files. Credentials are excluded from model-facing argument schemas
and tool serialization.

## Tools and parameters

| Class | Tool name | Required input | Optional parameters |
| --- | --- | --- | --- |
| `FlashDataGoogleSearch` | `flashdata_google_search` | `query` | `num=10` (1–100), `page=1` (1–100), `autocorrect=True`, `gl`, `hl`, `location`, `tbs` |
| `FlashDataYouTubeSearch` | `flashdata_youtube_search` | `query` | `max_results=10` (1–20) |
| `FlashDataYouTubeMetadata` | `flashdata_youtube_metadata` | `video_id` | `include_chapters=True`, `include_formats=True` |
| `FlashDataYouTubeTranscript` | `flashdata_youtube_transcript` | `video_id` | `language="en"`, `auto=True` |

Queries must contain 1–2,000 characters after trimming. `gl` is a two-letter country
code; `hl` and `language` accept language codes; `location` and `tbs` accept up to
200 characters. A video input accepts an 11-character ID or a YouTube watch,
shorts, embed, live, or `youtu.be` URL. Only the video ID is sent to FlashData.

For transcripts, `auto=False` requests manually authored captions and `auto=True`
requests automatic captions. There is no automatic language or caption fallback.

```python
import asyncio
from langchain_flashdata import FlashDataYouTubeTranscript


async def main():
    result = await FlashDataYouTubeTranscript().ainvoke(
        {
            "video_id": "https://youtu.be/dQw4w9WgXcQ",
            "language": "en",
            "auto": False,
        }
    )
    print(result["results"][0]["segments"])


asyncio.run(main())
```

## Use with a LangChain / LangGraph agent

The [research example](https://github.com/flashdata-dev/langchain-flashdata/blob/main/examples/research_agent.py) uses `create_agent`, which runs
on LangGraph. The model chooses tools and arguments from the question. A tool call
limit bounds the number of queries; it does not set a credit or dollar limit.

```bash
git clone https://github.com/flashdata-dev/langchain-flashdata.git
cd langchain-flashdata
pip install '.[examples]'
export OPENAI_API_KEY='YOUR_MODEL_PROVIDER_KEY'
export OPENAI_MODEL='YOUR_TOOL_CALLING_MODEL'
# Optional for a Chat Completions compatible provider:
# export OPENAI_BASE_URL='https://YOUR_PROVIDER/v1'

python examples/research_agent.py \
  'Find recent LangGraph tutorials using Google Search. Request 3 results and cite their URLs.' \
  --max-tool-calls 1
```

This example uses `ChatOpenAI` with the Chat Completions API. Use a model that
supports tool calling. You can replace that model adapter with another LangChain
chat model. The FlashData tools do not depend on a particular model provider.

For a custom graph, pass the tools from `FlashDataToolkit().get_tools()` to
LangGraph's `ToolNode`. Use `handle_tool_errors=False` to propagate query failures
and stop execution before a model can resubmit an unknown-outcome query. Avoid
automatic graph retries or replay of paid tool nodes.

```python
from langchain_flashdata import FlashDataToolkit
from langgraph.prebuilt import ToolNode

tools = FlashDataToolkit().get_tools()
tool_node = ToolNode(tools, handle_tool_errors=False)
```

See [the examples guide](https://github.com/flashdata-dev/langchain-flashdata/blob/main/examples/README.md) for direct tool calls, transcript
research, and the hosted MCP alternative.

## Output and errors

`invoke` and `ainvoke` return the complete API response dictionary. The envelope
contains `source`, `results`, and available usage/timestamp fields; some successful
responses omit `status`. Tool-call invocations produce a LangChain `ToolMessage`
containing the JSON response.

| Operation | Data location |
| --- | --- |
| Google Search | `results[0].organic` |
| YouTube search | `results[0].results` |
| Video metadata | `results[0]` |
| Transcript | `results[0].segments`, with available `fullText`, `languageCode`, and `isAutoGenerated` |

Invalid arguments fail locally before sending a request. API failures raise
`FlashDataError`, a LangChain `ToolException`. HTTP 401 indicates an invalid key,
402 insufficient credits, 403 a source/access restriction, and 429 a rate/quota
limit. Upstream error bodies and credentials are not included in exception messages.

Paid POST requests are not automatically retried or redirected. A timeout,
connection failure, unreadable result, or unexpected response may occur after a
query was submitted and charged: check Jobs in the FlashData console before
submitting again. The client connects directly to FlashData over HTTPS, with a
15-second connect timeout and a 120-second I/O timeout. Environment proxy settings
are not used.

## Existing MCP users

You can also connect LangChain to the existing hosted MCP endpoint at
`https://data.flashdata.dev/mcp` using the `X-API-Key` header. The native Python
tools above cover four query operations; the MCP catalog also contains account
and job operations and varies with key scopes. See [hosted_mcp.py](https://github.com/flashdata-dev/langchain-flashdata/blob/main/examples/hosted_mcp.py).
The example uses the current `langchain[mcp]` API, which LangChain labels beta.

## Development

```bash
uv sync --extra examples
uv run --extra examples pytest --disable-socket --allow-unix-socket
uv run ruff check .
uv run ruff format --check .
uv build
uv run twine check dist/*
```

Tests include LangChain's standard tool suite, request contracts, validation,
sync/async calls, `ToolMessage` delivery, Agent error propagation, and tool budgets.
Unit tests do not call external services. Run the four paid API integration tests
explicitly with `FLASHDATA_API_KEY` configured:

```bash
FLASHDATA_RUN_LIVE=1 uv run --extra examples pytest tests/integration_tests -q
```

Release instructions: [RELEASING.md](https://github.com/flashdata-dev/langchain-flashdata/blob/main/RELEASING.md).
Data handling: [PRIVACY.md](https://github.com/flashdata-dev/langchain-flashdata/blob/main/PRIVACY.md).
License: [MIT](https://github.com/flashdata-dev/langchain-flashdata/blob/main/LICENSE).
Support: [support@flashdata.dev](mailto:support@flashdata.dev).
