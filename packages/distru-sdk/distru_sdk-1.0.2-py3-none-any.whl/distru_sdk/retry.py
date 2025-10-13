"""Custom retry strategies for Distru SDK.

Provides configurable retry policies for handling transient failures.
"""

import random
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, Type, Union

from distru_sdk import exceptions


class RetryStrategy(ABC):
    """Abstract base class for retry strategies."""

    @abstractmethod
    def should_retry(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> bool:
        """Determine if request should be retried.

        Args:
            attempt: Current attempt number (0-indexed)
            exception: Exception that occurred
            response_code: HTTP response code (if available)

        Returns:
            True if request should be retried
        """
        pass

    @abstractmethod
    def get_delay(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> float:
        """Get delay before next retry.

        Args:
            attempt: Current attempt number (0-indexed)
            exception: Exception that occurred
            response_code: HTTP response code (if available)

        Returns:
            Delay in seconds
        """
        pass


class ExponentialBackoff(RetryStrategy):
    """Exponential backoff retry strategy.

    Delay grows exponentially: base * (multiplier ^ attempt)

    Example:
        >>> strategy = ExponentialBackoff(
        ...     max_retries=3,
        ...     base_delay=1.0,
        ...     multiplier=2.0,
        ...     max_delay=10.0
        ... )
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        multiplier: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        retry_on: tuple = (
            exceptions.RateLimitError,
            exceptions.ServerError,
            exceptions.NetworkError,
            exceptions.TimeoutError,
        ),
    ) -> None:
        """Initialize exponential backoff strategy.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            multiplier: Multiplier for exponential growth
            max_delay: Maximum delay in seconds
            jitter: Add random jitter to prevent thundering herd
            retry_on: Tuple of exception types to retry on
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter
        self.retry_on = retry_on

    def should_retry(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False

        # Check if exception type should be retried
        if not isinstance(exception, self.retry_on):
            return False

        # Always retry rate limits and server errors
        if isinstance(exception, (exceptions.RateLimitError, exceptions.ServerError)):
            return True

        # Retry network and timeout errors
        if isinstance(exception, (exceptions.NetworkError, exceptions.TimeoutError)):
            return True

        return False

    def get_delay(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> float:
        """Get delay before next retry."""
        # Check for Retry-After header on rate limit
        if isinstance(exception, exceptions.RateLimitError) and exception.retry_after:
            return float(exception.retry_after)

        # Calculate exponential backoff
        delay = min(self.base_delay * (self.multiplier**attempt), self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class LinearBackoff(RetryStrategy):
    """Linear backoff retry strategy.

    Delay increases linearly: base + (increment * attempt)

    Example:
        >>> strategy = LinearBackoff(
        ...     max_retries=3,
        ...     base_delay=1.0,
        ...     increment=1.0
        ... )
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        increment: float = 1.0,
        max_delay: float = 60.0,
        retry_on: tuple = (
            exceptions.RateLimitError,
            exceptions.ServerError,
            exceptions.NetworkError,
            exceptions.TimeoutError,
        ),
    ) -> None:
        """Initialize linear backoff strategy.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            increment: Delay increment per attempt
            max_delay: Maximum delay in seconds
            retry_on: Tuple of exception types to retry on
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.increment = increment
        self.max_delay = max_delay
        self.retry_on = retry_on

    def should_retry(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False

        return isinstance(exception, self.retry_on)

    def get_delay(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> float:
        """Get delay before next retry."""
        # Check for Retry-After header
        if isinstance(exception, exceptions.RateLimitError) and exception.retry_after:
            return float(exception.retry_after)

        return min(self.base_delay + (self.increment * attempt), self.max_delay)


class FixedDelay(RetryStrategy):
    """Fixed delay retry strategy.

    Uses same delay for all retries.

    Example:
        >>> strategy = FixedDelay(max_retries=3, delay=2.0)
    """

    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        retry_on: tuple = (
            exceptions.RateLimitError,
            exceptions.ServerError,
            exceptions.NetworkError,
            exceptions.TimeoutError,
        ),
    ) -> None:
        """Initialize fixed delay strategy.

        Args:
            max_retries: Maximum number of retry attempts
            delay: Fixed delay in seconds
            retry_on: Tuple of exception types to retry on
        """
        self.max_retries = max_retries
        self.delay = delay
        self.retry_on = retry_on

    def should_retry(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.max_retries:
            return False

        return isinstance(exception, self.retry_on)

    def get_delay(
        self,
        attempt: int,
        exception: Exception,
        response_code: Optional[int] = None,
    ) -> float:
        """Get delay before next retry."""
        # Check for Retry-After header
        if isinstance(exception, exceptions.RateLimitError) and exception.retry_after:
            return float(exception.retry_after)

        return self.delay


class CustomRetry:
    """Decorator for adding custom retry logic to functions.

    Example:
        >>> @CustomRetry(strategy=ExponentialBackoff(max_retries=3))
        ... def fetch_data():
        ...     return client.products.list()
    """

    def __init__(self, strategy: RetryStrategy) -> None:
        """Initialize custom retry decorator.

        Args:
            strategy: Retry strategy to use
        """
        self.strategy = strategy

    def __call__(self, func: Callable) -> Callable:
        """Decorate function with retry logic.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """

        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    response_code = getattr(e, "status_code", None)

                    if not self.strategy.should_retry(attempt, e, response_code):
                        raise

                    delay = self.strategy.get_delay(attempt, e, response_code)
                    time.sleep(delay)
                    attempt += 1

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
