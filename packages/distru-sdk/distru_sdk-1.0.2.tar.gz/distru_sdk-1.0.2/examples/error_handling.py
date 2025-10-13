"""Error handling examples for Distru SDK.

This example demonstrates various error handling patterns.
"""

import logging
from distru_sdk import DistruClient
from distru_sdk.exceptions import (
    DistruAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
)
from distru_sdk.retry import ExponentialBackoff, LinearBackoff, FixedDelay, CustomRetry


def example_basic_error_handling():
    """Example: Basic error handling with try/except."""
    client = DistruClient(api_token="your_api_token")

    try:
        product = client.products.get("invalid_id")
        print(f"Product: {product.name}")

    except NotFoundError as e:
        print(f"Product not found: {e}")

    except ValidationError as e:
        print(f"Validation error: {e}")
        print(f"Details: {e.details}")

    except DistruAPIError as e:
        print(f"API error: {e}")
        print(f"Status code: {e.status_code}")
        print(f"Response data: {e.response_data}")

    finally:
        client.close()


def example_specific_error_handling():
    """Example: Handle specific error types differently."""
    client = DistruClient(api_token="your_api_token")

    try:
        # Try to create a product
        product = client.products.create({
            "name": "New Product",
            "sku": "SKU-001",
        })
        print(f"Created product: {product.id}")

    except AuthenticationError as e:
        print("Authentication failed. Check your API token.")
        print(f"Error: {e}")

    except AuthorizationError as e:
        print("Not authorized. Check your permissions.")
        print(f"Error: {e}")

    except ValidationError as e:
        print("Validation failed. Check your input data.")
        print(f"Error: {e}")
        print(f"Validation details: {e.details}")

    except RateLimitError as e:
        print("Rate limit exceeded. Waiting before retry...")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
            import time
            time.sleep(e.retry_after)
            # Retry the request
            product = client.products.create({
                "name": "New Product",
                "sku": "SKU-001",
            })

    except ServerError as e:
        print("Server error occurred. Try again later.")
        print(f"Error: {e}")

    except NetworkError as e:
        print("Network error. Check your connection.")
        print(f"Error: {e}")

    except TimeoutError as e:
        print("Request timed out.")
        print(f"Timeout was: {e.timeout} seconds")

    except DistruAPIError as e:
        print("Unexpected API error occurred.")
        print(f"Error: {e}")

    finally:
        client.close()


def example_retry_with_exponential_backoff():
    """Example: Retry with exponential backoff strategy."""
    from distru_sdk.retry import ExponentialBackoff, CustomRetry

    client = DistruClient(api_token="your_api_token")

    # Create retry strategy
    strategy = ExponentialBackoff(
        max_retries=3,
        base_delay=1.0,
        multiplier=2.0,
        max_delay=10.0,
    )

    # Decorate function with retry logic
    @CustomRetry(strategy=strategy)
    def fetch_product(product_id):
        return client.products.get(product_id)

    try:
        product = fetch_product("product_123")
        print(f"Product: {product.name}")

    except DistruAPIError as e:
        print(f"Failed after retries: {e}")

    finally:
        client.close()


def example_retry_with_linear_backoff():
    """Example: Retry with linear backoff strategy."""
    from distru_sdk.retry import LinearBackoff, CustomRetry

    client = DistruClient(api_token="your_api_token")

    # Linear backoff: 1s, 2s, 3s delays
    strategy = LinearBackoff(
        max_retries=3,
        base_delay=1.0,
        increment=1.0,
    )

    @CustomRetry(strategy=strategy)
    def create_order(order_data):
        return client.orders.create(order_data)

    try:
        order = create_order({
            "contact_id": "contact_123",
            "items": [{"product_id": "prod_456", "quantity": 1}],
        })
        print(f"Order created: {order.id}")

    except DistruAPIError as e:
        print(f"Failed to create order: {e}")

    finally:
        client.close()


def example_retry_with_fixed_delay():
    """Example: Retry with fixed delay strategy."""
    from distru_sdk.retry import FixedDelay, CustomRetry

    client = DistruClient(api_token="your_api_token")

    # Fixed 2 second delay between retries
    strategy = FixedDelay(
        max_retries=3,
        delay=2.0,
    )

    @CustomRetry(strategy=strategy)
    def update_product(product_id, data):
        return client.products.update(product_id, data)

    try:
        product = update_product("prod_123", {"name": "Updated Name"})
        print(f"Product updated: {product.name}")

    except DistruAPIError as e:
        print(f"Failed to update product: {e}")

    finally:
        client.close()


def example_logging_errors():
    """Example: Log errors for debugging."""
    import logging

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    client = DistruClient(api_token="your_api_token")

    try:
        product = client.products.get("invalid_id")

    except NotFoundError as e:
        logger.warning(f"Product not found: {e}")

    except ValidationError as e:
        logger.error(f"Validation error: {e}", extra={"details": e.details})

    except DistruAPIError as e:
        logger.error(
            f"API error occurred",
            exc_info=True,
            extra={
                "status_code": e.status_code,
                "response_data": e.response_data,
            }
        )

    finally:
        client.close()


def example_graceful_degradation():
    """Example: Gracefully degrade when API is unavailable."""
    client = DistruClient(api_token="your_api_token")

    def get_product_with_fallback(product_id, default=None):
        """Get product with fallback to default value."""
        try:
            return client.products.get(product_id)

        except NotFoundError:
            print(f"Product {product_id} not found, using default")
            return default

        except (ServerError, NetworkError, TimeoutError) as e:
            print(f"API unavailable ({e}), using default")
            return default

        except DistruAPIError as e:
            print(f"API error ({e}), using default")
            return default

    # Use with fallback
    product = get_product_with_fallback(
        "prod_123",
        default={"id": "prod_123", "name": "Unknown Product"}
    )

    print(f"Product: {product.get('name') if isinstance(product, dict) else product.name}")

    client.close()


def example_batch_error_handling():
    """Example: Handle errors in batch operations."""
    from distru_sdk.batch import BatchProcessor

    client = DistruClient(api_token="your_api_token")

    # Track errors
    errors = []

    def on_error(item, error):
        """Error handler for batch processing."""
        errors.append({
            "item": item,
            "error": str(error),
            "error_type": type(error).__name__,
        })

    # Create processor with error handler
    processor = BatchProcessor(
        processor=client.products.create,
        batch_size=5,
        on_error=on_error,
    )

    products = [
        {"name": "Product 1", "sku": "SKU-001"},
        {"name": "Product 2"},  # Missing SKU - might fail
        {"name": "Product 3", "sku": "SKU-003"},
    ]

    # Process with error handling
    results = processor.process(products, raise_on_error=False)

    # Report results
    successes = [r for r in results if r is not None]
    print(f"Successfully created: {len(successes)}")
    print(f"Failed: {len(errors)}")

    for error in errors:
        print(f"  - {error['item'].get('name')}: {error['error_type']} - {error['error']}")

    client.close()


def example_circuit_breaker_pattern():
    """Example: Implement circuit breaker pattern for fault tolerance."""
    import time
    from enum import Enum

    class CircuitState(Enum):
        CLOSED = "closed"  # Normal operation
        OPEN = "open"      # Too many failures, reject requests
        HALF_OPEN = "half_open"  # Testing if service recovered

    class CircuitBreaker:
        def __init__(self, failure_threshold=5, timeout=60):
            self.failure_threshold = failure_threshold
            self.timeout = timeout
            self.failures = 0
            self.last_failure_time = None
            self.state = CircuitState.CLOSED

        def call(self, func, *args, **kwargs):
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)

                # Success - reset if in half-open
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failures = 0

                return result

            except (ServerError, NetworkError, TimeoutError) as e:
                self.failures += 1
                self.last_failure_time = time.time()

                if self.failures >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    print(f"Circuit breaker opened after {self.failures} failures")

                raise

    # Use circuit breaker
    client = DistruClient(api_token="your_api_token")
    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

    try:
        product = circuit_breaker.call(client.products.get, "prod_123")
        print(f"Product: {product.name}")

    except Exception as e:
        print(f"Circuit breaker prevented call or call failed: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    print("Error Handling Examples\n")

    # Run examples (comment out what you don't need)
    # example_basic_error_handling()
    # example_specific_error_handling()
    # example_retry_with_exponential_backoff()
    # example_retry_with_linear_backoff()
    # example_retry_with_fixed_delay()
    # example_logging_errors()
    # example_graceful_degradation()
    # example_batch_error_handling()
    # example_circuit_breaker_pattern()

    print("\nDone!")
