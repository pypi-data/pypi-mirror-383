"""Shared HTTP client helpers for Raindrop.io API access."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

import httpx

from raindropio_mcp.utils.exceptions import (
    APIError,
    NetworkError,
    NotFoundError,
    RateLimitError,
)

if TYPE_CHECKING:
    from raindropio_mcp.config.settings import RaindropSettings

logger = logging.getLogger(__name__)

_JSON = dict[str, Any] | list[Any] | None
_ResponseHook = Callable[[httpx.Response], None]


@dataclass(slots=True)
class RequestMetrics:
    """Lightweight request metrics captured for observability."""

    method: str
    url: str
    status_code: int
    duration_seconds: float
    retry_count: int


class BaseHTTPClient:
    """Async HTTP client with retry, error handling, and metrics."""

    def __init__(
        self,
        settings: RaindropSettings,
        *,
        on_response: _ResponseHook | None = None,
    ) -> None:
        self._settings = settings
        self._retry_config = settings.retry
        self._on_response = on_response
        self._client = httpx.AsyncClient(**settings.http_client_config())
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> BaseHTTPClient:  # pragma: no cover - convenience
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:  # pragma: no cover
        await self.close()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: _JSON = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        expected_status: tuple[int, ...] | None = None,
    ) -> httpx.Response:
        url = path if path.startswith("http") else f"{self._settings.base_url}{path}"
        attempt = 0
        backoff = self._retry_config.backoff_factor

        while True:
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    data=data,
                    headers=headers,
                )
            except httpx.TimeoutException as exc:
                if attempt >= self._retry_config.total:
                    raise NetworkError("Request timed out") from exc
                await asyncio.sleep(backoff * (2**attempt))
                attempt += 1
                continue
            except httpx.TransportError as exc:
                if attempt >= self._retry_config.total:
                    raise NetworkError("Transport error talking to Raindrop.io") from exc
                await asyncio.sleep(backoff * (2**attempt))
                attempt += 1
                continue

            if self._on_response:
                try:
                    self._on_response(response)
                except Exception:  # pragma: no cover - logging only
                    logger.exception("Response hook raised; continuing")

            if expected_status and response.status_code not in expected_status:
                # Fall through to error handling
                error = self._map_error(method, url, response)
                if self._should_retry(response.status_code, attempt):
                    await asyncio.sleep(backoff * (2**attempt))
                    attempt += 1
                    continue
                raise error

            if 200 <= response.status_code < 300:
                return response

            error = self._map_error(method, url, response)
            if self._should_retry(response.status_code, attempt):
                await asyncio.sleep(backoff * (2**attempt))
                attempt += 1
                continue
            raise error

    async def get_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: _JSON = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        expected_status: tuple[int, ...] | None = None,
    ) -> dict[str, Any]:
        response = await self.request(
            method,
            path,
            params=params,
            json_body=json_body,
            data=data,
            headers=headers,
            expected_status=expected_status,
        )

        try:
            json_data = response.json()
            if not isinstance(json_data, dict):
                raise APIError(
                    "Raindrop.io returned invalid JSON format (expected object)",
                    status_code=response.status_code,
                    response_data=json_data,
                )
            return json_data
        except json.JSONDecodeError as exc:  # pragma: no cover - rarely hit
            raise APIError(
                "Raindrop.io returned invalid JSON",
                status_code=response.status_code,
                response_data=response.text,
            ) from exc

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        retryable_codes = self._retry_config.status_forcelist
        return bool(status_code in retryable_codes and attempt < self._retry_config.total)

    def _map_error(self, method: str, url: str, response: httpx.Response) -> APIError:
        status = response.status_code
        details: dict[str, Any] = {
            "method": method,
            "url": url,
        }
        try:
            payload = response.json()
        except json.JSONDecodeError:
            payload = {"body": response.text}

        if status == 404:
            return NotFoundError(
                "Resource not found",
                details={**details, "payload": payload},
            )
        if status == 401:
            return APIError(
                "Authentication failed; check RAINDROP_TOKEN",
                status_code=status,
                response_data=payload,
                details=details,
            )
        if status == 403:
            return APIError(
                "Not authorised to perform this operation",
                status_code=status,
                response_data=payload,
                details=details,
            )
        if status == 429:
            retry_after = response.headers.get("Retry-After")
            return RateLimitError(
                "Rate limit exceeded",
                retry_after=float(retry_after) if retry_after else None,
                details={**details, "payload": payload},
            )

        return APIError(
            "Raindrop.io API request failed",
            status_code=status,
            response_data=payload,
            headers=dict(response.headers),
            details=details,
        )


__all__ = ["BaseHTTPClient", "RequestMetrics"]
