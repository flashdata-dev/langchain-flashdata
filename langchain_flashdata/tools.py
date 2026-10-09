"""FlashData tools implementing LangChain's BaseTool interface."""

import os
from typing import Any, ClassVar

from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from langchain_flashdata import _client
from langchain_flashdata._inputs import (
    GoogleSearchInput,
    YouTubeMetadataInput,
    YouTubeSearchInput,
    YouTubeTranscriptInput,
)


def _key_from_env() -> SecretStr:
    value = os.environ.get("FLASHDATA_API_KEY", "").strip()
    if not value:
        raise ValueError("Set FLASHDATA_API_KEY or pass api_key when constructing the tool.")
    return SecretStr(value)


class _FlashDataTool(BaseTool):
    model_config = ConfigDict(hide_input_in_errors=True)
    api_key: SecretStr = Field(default_factory=_key_from_env, exclude=True, repr=False)
    source: ClassVar[str]

    @field_validator("api_key")
    @classmethod
    def _validate_key(cls, value: SecretStr) -> SecretStr:
        key = value.get_secret_value().strip()
        if not key:
            raise ValueError("FlashData API key must not be empty.")
        return SecretStr(key)

    def _payload(self, values: dict[str, Any]) -> dict[str, Any]:
        # Apply defaults again: BaseTool only forwards explicitly supplied arguments.
        params = self.get_input_schema().model_validate(values).model_dump(exclude_none=True)
        primary = "query" if "query" in params else "video_id"
        return {"source": self.source, primary: params.pop(primary), "params": params}

    def _run(self, **kwargs: Any) -> dict[str, Any]:
        return _client.query(self.api_key, self._payload(kwargs))

    async def _arun(self, **kwargs: Any) -> dict[str, Any]:
        return await _client.aquery(self.api_key, self._payload(kwargs))


class FlashDataGoogleSearch(_FlashDataTool):
    """Search Google for current web results with source URLs."""

    name: str = "flashdata_google_search"
    description: str = (
        "Search Google for current web results, titles, snippets and source URLs. "
        "Uses FlashData credits. Do not repeat a query after an unknown outcome; check Jobs first."
    )
    args_schema: type[BaseModel] = GoogleSearchInput
    source: ClassVar[str] = "google_search"


class FlashDataYouTubeSearch(_FlashDataTool):
    """Search YouTube videos."""

    name: str = "flashdata_youtube_search"
    description: str = (
        "Find YouTube videos by search query. Returns video IDs and available video metadata. "
        "Uses FlashData credits. Do not repeat a query after an unknown outcome; check Jobs first."
    )
    args_schema: type[BaseModel] = YouTubeSearchInput
    source: ClassVar[str] = "youtube_search"


class FlashDataYouTubeMetadata(_FlashDataTool):
    """Retrieve metadata for a YouTube video."""

    name: str = "flashdata_youtube_metadata"
    description: str = (
        "Get YouTube video metadata by ID or URL, with optional chapters and format metadata. "
        "Uses FlashData credits. Do not repeat a query after an unknown outcome; check Jobs first."
    )
    args_schema: type[BaseModel] = YouTubeMetadataInput
    source: ClassVar[str] = "youtube_metadata"


class FlashDataYouTubeTranscript(_FlashDataTool):
    """Retrieve captions for a YouTube video."""

    name: str = "flashdata_youtube_transcript"
    description: str = (
        "Get a YouTube transcript with timestamped segments by video ID or URL. Specify language "
        "and auto=true for automatic captions or auto=false for manual captions. "
        "No implicit fallback. "
        "Uses FlashData credits. Do not repeat a query after an unknown outcome; check Jobs first."
    )
    args_schema: type[BaseModel] = YouTubeTranscriptInput
    source: ClassVar[str] = "youtube_transcript"
