"""Opt-in live checks. Four queries consume credits; CI does not run these."""

import os

import pytest

from langchain_flashdata import (
    FlashDataGoogleSearch,
    FlashDataYouTubeMetadata,
    FlashDataYouTubeSearch,
    FlashDataYouTubeTranscript,
)

pytestmark = pytest.mark.skipif(
    os.environ.get("FLASHDATA_RUN_LIVE") != "1", reason="Set FLASHDATA_RUN_LIVE=1 to spend credits."
)


def test_google_search():
    result = FlashDataGoogleSearch().invoke({"query": "LangChain tools documentation", "num": 3})
    assert result["source"] == "google_search"
    assert result["results"][0]["organic"]


@pytest.mark.asyncio
async def test_youtube_search():
    result = await FlashDataYouTubeSearch().ainvoke(
        {"query": "LangGraph tutorial", "max_results": 2}
    )
    assert result["source"] == "youtube_search"
    assert result["results"][0]["results"]


def test_youtube_metadata():
    result = FlashDataYouTubeMetadata().invoke(
        {"video_id": "https://youtu.be/dQw4w9WgXcQ", "include_formats": False}
    )
    assert result["source"] == "youtube_metadata"
    assert result["results"][0]["title"]


@pytest.mark.asyncio
async def test_youtube_transcript():
    result = await FlashDataYouTubeTranscript().ainvoke({"video_id": "dQw4w9WgXcQ", "auto": False})
    assert result["source"] == "youtube_transcript"
    assert result["results"][0]["segments"]
