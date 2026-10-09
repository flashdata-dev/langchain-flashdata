"""HTTP transport for the FlashData realtime query API."""

from typing import Any
from uuid import uuid4

import httpx
from langchain_core.tools import ToolException
from pydantic import SecretStr

QUERY_URL = "https://data.flashdata.dev/v1/queries/realtime"
TIMEOUT = httpx.Timeout(120.0, connect=15.0)
UNKNOWN_OUTCOME = (
    "The FlashData query outcome is unknown and may already be charged. "
    "Check Jobs in the FlashData console before submitting again. No automatic retry was made."
)


class FlashDataError(ToolException):
    """An actionable error without credentials or raw upstream error bodies."""


def _headers(api_key: SecretStr) -> dict[str, str]:
    return {
        "X-API-Key": api_key.get_secret_value(),
        "X-Request-Id": str(uuid4()),
        "Accept": "application/json",
        "User-Agent": "langchain-flashdata/0.1.0",
    }


def _result(response: httpx.Response) -> dict[str, Any]:
    if response.status_code != 200:
        messages = {
            401: "FlashData rejected the API key. Check FLASHDATA_API_KEY.",
            402: "Insufficient FlashData credits. Add credits in the FlashData console.",
            403: "This FlashData account or key cannot access the requested source.",
            429: "FlashData rate or quota limit reached. Wait before trying again.",
        }
        message = messages.get(response.status_code, UNKNOWN_OUTCOME)
        raise FlashDataError(f"{message} HTTP {response.status_code}.")
    try:
        data = response.json()
    except ValueError:
        raise FlashDataError(UNKNOWN_OUTCOME) from None
    if not isinstance(data, dict):
        raise FlashDataError(UNKNOWN_OUTCOME)
    job = data.get("job")
    if data.get("status") == "failed" or (isinstance(job, dict) and job.get("status") == "failed"):
        raise FlashDataError("FlashData could not complete the query. Check its details in Jobs.")
    if data.get("status") not in (None, "done", "completed") or not isinstance(
        data.get("results"), list
    ):
        raise FlashDataError(UNKNOWN_OUTCOME)
    return data


def query(api_key: SecretStr, payload: dict[str, Any]) -> dict[str, Any]:
    """Submit exactly one query. A lost POST response may already be billed."""
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=False, trust_env=False) as client:
            response = client.post(QUERY_URL, json=payload, headers=_headers(api_key))
    except httpx.HTTPError:
        raise FlashDataError(UNKNOWN_OUTCOME) from None
    return _result(response)


async def aquery(api_key: SecretStr, payload: dict[str, Any]) -> dict[str, Any]:
    """Submit one query using native async I/O without retries or redirects."""
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT, follow_redirects=False, trust_env=False
        ) as client:
            response = await client.post(QUERY_URL, json=payload, headers=_headers(api_key))
    except httpx.HTTPError:
        raise FlashDataError(UNKNOWN_OUTCOME) from None
    return _result(response)
