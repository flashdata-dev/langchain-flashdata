"""Toolkit containing FlashData's four native query tools."""

from langchain_core.tools import BaseTool, BaseToolkit
from pydantic import ConfigDict, Field, SecretStr

from langchain_flashdata.tools import (
    FlashDataGoogleSearch,
    FlashDataYouTubeMetadata,
    FlashDataYouTubeSearch,
    FlashDataYouTubeTranscript,
    _key_from_env,
)


class FlashDataToolkit(BaseToolkit):
    """Create the four FlashData tools with a shared API key."""

    model_config = ConfigDict(hide_input_in_errors=True)
    api_key: SecretStr = Field(default_factory=_key_from_env, exclude=True, repr=False)

    def get_tools(self) -> list[BaseTool]:
        """Return Google Search, YouTube Search, Metadata, and Transcript tools."""
        return [
            tool(api_key=self.api_key)
            for tool in (
                FlashDataGoogleSearch,
                FlashDataYouTubeSearch,
                FlashDataYouTubeMetadata,
                FlashDataYouTubeTranscript,
            )
        ]
