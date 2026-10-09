from langchain_tests.unit_tests.tools import ToolsUnitTests

from langchain_flashdata import (
    FlashDataGoogleSearch,
    FlashDataYouTubeMetadata,
    FlashDataYouTubeSearch,
    FlashDataYouTubeTranscript,
)


class _FlashDataStandard(ToolsUnitTests):
    @property
    def tool_constructor_params(self):
        return {"api_key": "test-secret"}

    @property
    def init_from_env_params(self):
        return {"FLASHDATA_API_KEY": "env-secret"}, {}, {"api_key": "env-secret"}


class TestGoogleSearch(_FlashDataStandard):
    @property
    def tool_constructor(self):
        return FlashDataGoogleSearch

    @property
    def tool_invoke_params_example(self):
        return {"query": "LangChain tools"}


class TestYouTubeSearch(_FlashDataStandard):
    @property
    def tool_constructor(self):
        return FlashDataYouTubeSearch

    @property
    def tool_invoke_params_example(self):
        return {"query": "LangGraph tutorial"}


class TestYouTubeMetadata(_FlashDataStandard):
    @property
    def tool_constructor(self):
        return FlashDataYouTubeMetadata

    @property
    def tool_invoke_params_example(self):
        return {"video_id": "dQw4w9WgXcQ"}


class TestYouTubeTranscript(_FlashDataStandard):
    @property
    def tool_constructor(self):
        return FlashDataYouTubeTranscript

    @property
    def tool_invoke_params_example(self):
        return {"video_id": "https://youtu.be/dQw4w9WgXcQ", "language": "en", "auto": False}
