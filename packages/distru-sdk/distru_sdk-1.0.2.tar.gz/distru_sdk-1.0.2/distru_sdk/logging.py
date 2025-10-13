"""Request/response logging utilities for Distru SDK.

Provides configurable logging for debugging and monitoring.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

import httpx


class RequestLogger:
    """HTTP request/response logger.

    Example:
        >>> logger = RequestLogger(level=logging.DEBUG)
        >>> logger.log_request("GET", "/products", params={"page": 1})
        >>> logger.log_response(response, duration=0.5)
    """

    def __init__(
        self,
        name: str = "distru_sdk",
        level: int = logging.INFO,
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_length: int = 1000,
    ) -> None:
        """Initialize request logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            max_body_length: Maximum length of body to log
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length

        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Log outgoing request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            body: Request body
            headers: Request headers
        """
        msg_parts = [f"{method} {url}"]

        if params:
            msg_parts.append(f"params={json.dumps(params)}")

        if self.log_request_body and body:
            body_str = json.dumps(body)
            if len(body_str) > self.max_body_length:
                body_str = body_str[: self.max_body_length] + "..."
            msg_parts.append(f"body={body_str}")

        if headers:
            # Redact sensitive headers
            safe_headers = self._redact_headers(headers)
            msg_parts.append(f"headers={json.dumps(safe_headers)}")

        self.logger.debug(" | ".join(msg_parts))

    def log_response(
        self,
        response: httpx.Response,
        duration: Optional[float] = None,
    ) -> None:
        """Log API response.

        Args:
            response: HTTP response object
            duration: Request duration in seconds
        """
        msg_parts = [
            f"{response.status_code} {response.request.method} {response.request.url}"
        ]

        if duration is not None:
            msg_parts.append(f"duration={duration:.3f}s")

        if self.log_response_body and response.content:
            try:
                body = response.json()
                body_str = json.dumps(body)
                if len(body_str) > self.max_body_length:
                    body_str = body_str[: self.max_body_length] + "..."
                msg_parts.append(f"body={body_str}")
            except Exception:
                # If not JSON, log first N bytes
                body_str = response.text[: self.max_body_length]
                if len(response.text) > self.max_body_length:
                    body_str += "..."
                msg_parts.append(f"body={body_str}")

        # Log at different levels based on status code
        if response.status_code < 400:
            self.logger.debug(" | ".join(msg_parts))
        elif response.status_code < 500:
            self.logger.warning(" | ".join(msg_parts))
        else:
            self.logger.error(" | ".join(msg_parts))

    def log_error(
        self,
        method: str,
        url: str,
        error: Exception,
        duration: Optional[float] = None,
    ) -> None:
        """Log request error.

        Args:
            method: HTTP method
            url: Request URL
            error: Exception that occurred
            duration: Request duration in seconds
        """
        msg_parts = [f"ERROR {method} {url}"]

        if duration is not None:
            msg_parts.append(f"duration={duration:.3f}s")

        msg_parts.append(f"error={type(error).__name__}: {str(error)}")

        self.logger.error(" | ".join(msg_parts))

    def _redact_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Redact sensitive headers.

        Args:
            headers: Headers dictionary

        Returns:
            Headers with sensitive values redacted
        """
        sensitive_keys = {"authorization", "api-key", "x-api-key", "cookie"}
        redacted = {}

        for key, value in headers.items():
            if key.lower() in sensitive_keys:
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = value

        return redacted


class LoggingHTTPClient(httpx.Client):
    """HTTP client with automatic request/response logging.

    Example:
        >>> logger = RequestLogger(level=logging.DEBUG)
        >>> client = LoggingHTTPClient(logger=logger, base_url="https://api.distru.com")
        >>> response = client.get("/products")
    """

    def __init__(self, logger: Optional[RequestLogger] = None, *args, **kwargs) -> None:
        """Initialize logging HTTP client.

        Args:
            logger: RequestLogger instance
            *args: Passed to httpx.Client
            **kwargs: Passed to httpx.Client
        """
        super().__init__(*args, **kwargs)
        self.logger = logger or RequestLogger()

    def request(self, method: str, url: str, *args, **kwargs) -> httpx.Response:
        """Make HTTP request with logging.

        Args:
            method: HTTP method
            url: Request URL
            *args: Passed to parent request method
            **kwargs: Passed to parent request method

        Returns:
            HTTP response
        """
        start_time = time.time()

        # Log request
        self.logger.log_request(
            method=method,
            url=str(url),
            params=kwargs.get("params"),
            body=kwargs.get("json"),
            headers=kwargs.get("headers"),
        )

        try:
            response = super().request(method, url, *args, **kwargs)
            duration = time.time() - start_time

            # Log response
            self.logger.log_response(response, duration=duration)

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Log error
            self.logger.log_error(method, str(url), e, duration=duration)

            raise


def configure_logging(
    level: int = logging.INFO,
    format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure SDK logging.

    Args:
        level: Logging level
        format: Log message format
        log_file: Optional file path for logging

    Returns:
        Configured logger

    Example:
        >>> import logging
        >>> logger = configure_logging(
        ...     level=logging.DEBUG,
        ...     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        ...     log_file="distru_sdk.log"
        ... )
    """
    logger = logging.getLogger("distru_sdk")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
