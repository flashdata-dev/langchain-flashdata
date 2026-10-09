"""Validated tool arguments. Credentials are never part of these schemas."""

import re
from typing import Annotated
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

Query = Annotated[str, Field(min_length=1, max_length=2000)]
Language = Annotated[str, Field(pattern=r"^[A-Za-z0-9-]{1,35}$")]


class _Input(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)


class GoogleSearchInput(_Input):
    """Google Search parameters."""

    query: Query = Field(description="Search query, between 1 and 2,000 characters.")
    num: int = Field(default=10, ge=1, le=100, description="Requested number of results.")
    page: int = Field(default=1, ge=1, le=100, description="Search result page.")
    autocorrect: bool = Field(default=True, description="Enable spelling autocorrection.")
    gl: Annotated[str, Field(pattern=r"^[A-Za-z]{2}$")] | None = Field(
        default=None, description="Two-letter country code, for example us."
    )
    hl: Language | None = Field(
        default=None, description="Interface language code, for example en."
    )
    location: Annotated[str, Field(max_length=200)] | None = Field(
        default=None, description="Optional geographic search location."
    )
    tbs: Annotated[str, Field(max_length=200)] | None = Field(
        default=None, description="Optional Google time filter, for example qdr:w."
    )


class YouTubeSearchInput(_Input):
    """YouTube video search parameters."""

    query: Query = Field(description="YouTube search query, between 1 and 2,000 characters.")
    max_results: int = Field(default=10, ge=1, le=20, description="Requested number of videos.")


class _VideoInput(_Input):
    video_id: str = Field(description="11-character YouTube video ID or a YouTube video URL.")

    @field_validator("video_id")
    @classmethod
    def normalize_video_id(cls, value: str) -> str:
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
            return value
        try:
            url = urlsplit(value)
            parts = url.path.split("/")
            candidate = ""
            if url.scheme in ("http", "https") and not url.username and not url.password:
                if url.hostname == "youtu.be" and (
                    len(parts) == 2 or (len(parts) == 3 and not parts[2])
                ):
                    candidate = parts[1]
                elif url.hostname in (
                    "youtube.com",
                    "www.youtube.com",
                    "m.youtube.com",
                    "music.youtube.com",
                ):
                    if url.path == "/watch":
                        candidate = parse_qs(url.query).get("v", [""])[0]
                    elif (len(parts) == 3 or (len(parts) == 4 and not parts[3])) and parts[1] in (
                        "shorts",
                        "embed",
                        "live",
                    ):
                        candidate = parts[2]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
                return candidate
        except ValueError:
            pass
        raise ValueError("Enter an 11-character YouTube ID or a youtube.com / youtu.be video URL.")


class YouTubeMetadataInput(_VideoInput):
    """YouTube metadata parameters."""

    include_chapters: bool = Field(default=True, description="Include available video chapters.")
    include_formats: bool = Field(default=True, description="Include available format metadata.")


class YouTubeTranscriptInput(_VideoInput):
    """YouTube transcript parameters; no implicit language or caption fallback."""

    language: Language = Field(default="en", description="Requested caption language code.")
    auto: bool = Field(
        default=True,
        description="True requests automatic captions; false requests manually authored captions.",
    )
