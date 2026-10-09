from unittest.mock import patch

import httpx
import pytest


@pytest.fixture
def mock_api():
    """Intercept HTTP at the transport boundary, keeping real request serialization."""
    sync_client, async_client = httpx.Client, httpx.AsyncClient

    def install(handler):
        transport = httpx.MockTransport(handler)
        return (
            patch(
                "langchain_flashdata._client.httpx.Client",
                side_effect=lambda **kwargs: sync_client(transport=transport, **kwargs),
            ),
            patch(
                "langchain_flashdata._client.httpx.AsyncClient",
                side_effect=lambda **kwargs: async_client(transport=transport, **kwargs),
            ),
        )

    return install
