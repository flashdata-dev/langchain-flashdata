"""Run one selected tool without a model. Each run can consume FlashData credits."""

import argparse
import asyncio
import json

from langchain_flashdata import FlashDataToolkit


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tool",
        choices=["google_search", "youtube_search", "youtube_metadata", "youtube_transcript"],
    )
    parser.add_argument("arguments", help='JSON arguments, for example: {"query": "LangChain"}')
    args = parser.parse_args()
    tools = {tool.name: tool for tool in FlashDataToolkit().get_tools()}
    result = await tools[f"flashdata_{args.tool}"].ainvoke(json.loads(args.arguments))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
