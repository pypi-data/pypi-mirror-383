"""Async client for the Distru API.

Provides asynchronous API access using httpx async client.
"""

import asyncio
import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from distru_sdk import exceptions


class AsyncDisruClient:
    """Async client for interacting with the Distru API.

    Provides async/await support for non-blocking API operations.

    Example:
        >>> import asyncio
        >>> async def main():
        ...     async with AsyncDisruClient(api_token="your_token") as client:
        ...         products = await client.products.list()
        ...         async for product in products.auto_paginate():
        ...             print(product.name)
        >>> asyncio.run(main())
    """

    DEFAULT_BASE_URL = "https://app.distru.com/public/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_token: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialize the async Distru API client.

        Args:
            api_token: Your Distru API token (Bearer token)
            base_url: Base URL for the API (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            http_client: Optional custom httpx.AsyncClient instance

        Raises:
            ValueError: If api_token is empty or None
        """
        if not api_token:
            raise ValueError("api_token is required")

        self.api_token = api_token
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create HTTP client
        if http_client:
            self._http_client = http_client
            self._owns_http_client = False
        else:
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=timeout,
                headers=self._get_default_headers(),
            )
            self._owns_http_client = True

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "distru-python-sdk/1.0.0",
        }

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON request body
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            AuthenticationError: On 401 responses
            AuthorizationError: On 403 responses
            NotFoundError: On 404 responses
            ValidationError: On 422 responses
            RateLimitError: On 429 responses (after retries exhausted)
            ServerError: On 5xx responses (after retries exhausted)
            NetworkError: On network/connection errors (after retries exhausted)
            TimeoutError: On request timeouts (after retries exhausted)
        """
        url = path if path.startswith("http") else urljoin(self.base_url + "/", path.lstrip("/"))

        retries = 0
        last_exception: Optional[Exception] = None

        while retries <= self.max_retries:
            try:
                response = await self._http_client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    **kwargs,
                )

                # Handle successful responses
                if response.status_code < 400:
                    return response

                # Check if we should retry
                if self._should_retry(response.status_code) and retries < self.max_retries:
                    delay = self._get_retry_delay(retries, response)
                    await asyncio.sleep(delay)
                    retries += 1
                    continue

                # No retry, raise the error
                self._handle_error_response(response)

            except (httpx.NetworkError, httpx.ConnectError) as e:
                last_exception = e
                if retries < self.max_retries:
                    delay = self._exponential_backoff(retries)
                    await asyncio.sleep(delay)
                    retries += 1
                    continue
                raise exceptions.NetworkError(
                    f"Network error: {str(e)}", original_error=e
                ) from e

            except httpx.TimeoutException as e:
                last_exception = e
                if retries < self.max_retries:
                    delay = self._exponential_backoff(retries)
                    await asyncio.sleep(delay)
                    retries += 1
                    continue
                raise exceptions.TimeoutError(
                    f"Request timed out after {self.timeout}s", timeout=self.timeout
                ) from e

        # Should never reach here, but just in case
        if last_exception:
            raise exceptions.NetworkError(
                "Max retries exceeded", original_error=last_exception
            ) from last_exception

        raise exceptions.DistruAPIError("Max retries exceeded")

    def _should_retry(self, status_code: int) -> bool:
        """Determine if request should be retried based on status code."""
        return status_code == 429 or status_code >= 500

    def _get_retry_delay(self, retry_count: int, response: httpx.Response) -> float:
        """Get delay before retrying request."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        return self._exponential_backoff(retry_count)

    def _exponential_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay."""
        return min(2**retry_count, 10.0)

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        status_code = response.status_code

        # Try to parse error response
        error_data = None
        try:
            error_data = response.json()
            error_message = error_data.get("error") or error_data.get("message") or str(error_data)
        except Exception:
            error_message = response.text or f"HTTP {status_code} error"

        # Raise specific exceptions
        if status_code == 401:
            raise exceptions.AuthenticationError(error_message, response_data=error_data)
        elif status_code == 403:
            raise exceptions.AuthorizationError(error_message, response_data=error_data)
        elif status_code == 404:
            raise exceptions.NotFoundError(error_message, response_data=error_data)
        elif status_code == 422:
            raise exceptions.ValidationError(error_message, response_data=error_data)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise exceptions.RateLimitError(
                error_message,
                retry_after=retry_after_int,
                response_data=error_data,
            )
        elif status_code >= 500:
            raise exceptions.ServerError(
                error_message,
                status_code=status_code,
                response_data=error_data,
            )
        else:
            raise exceptions.DistruAPIError(
                error_message,
                status_code=status_code,
                response_data=error_data,
            )

    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._owns_http_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> "AsyncDisruClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __del__(self) -> None:
        """Cleanup on deletion.

        Note: For proper async cleanup, use the context manager or call close() explicitly.
        This method cannot reliably perform async cleanup.
        """
        # Warn if the client wasn't properly closed
        if hasattr(self, "_owns_http_client") and self._owns_http_client:
            if hasattr(self, "_http_client") and not self._http_client.is_closed:
                import warnings
                warnings.warn(
                    "AsyncDisruClient was not properly closed. Use 'async with' context manager or call 'await client.close()' explicitly.",
                    ResourceWarning,
                    stacklevel=2
                )


class AsyncBaseResource:
    """Base class for async API resource endpoints."""

    def __init__(self, client: AsyncDisruClient) -> None:
        """Initialize resource with client.

        Args:
            client: AsyncDisruClient instance
        """
        self._client = client

    async def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async GET request."""
        response = await self._client.request("GET", path, params=params)
        return response.json()

    async def _post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async POST request."""
        response = await self._client.request("POST", path, json=json, params=params)
        return response.json()

    async def _patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async PATCH request."""
        response = await self._client.request("PATCH", path, json=json, params=params)
        return response.json()

    async def _delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async DELETE request."""
        response = await self._client.request("DELETE", path, params=params)
        if response.status_code == 204:
            return None
        return response.json() if response.content else None
