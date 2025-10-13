"""Batch operations examples for Distru SDK.

This example demonstrates various batch operation patterns.
"""

from distru_sdk import DistruClient
from distru_sdk.batch import BatchOperations, BatchProcessor, BulkIterator


def example_basic_batch_create():
    """Example: Create multiple products in batches."""
    client = DistruClient(api_token="your_api_token")
    batch_ops = BatchOperations(client)

    # Prepare product data
    products = [
        {"name": f"Product {i}", "sku": f"SKU-{i:04d}", "price": i * 10.0}
        for i in range(1, 51)  # 50 products
    ]

    print("Creating 50 products in batches of 10...")

    # Create products in batches
    results = batch_ops.create_multiple(
        client.products,
        products,
        batch_size=10,
        raise_on_error=False,
    )

    # Count results
    successes = [r for r in results if r is not None]
    failures = len(results) - len(successes)

    print(f"Created: {len(successes)}, Failed: {failures}")

    client.close()


def example_batch_update():
    """Example: Update multiple products in batches."""
    client = DistruClient(api_token="your_api_token")
    batch_ops = BatchOperations(client)

    # Prepare updates (must include 'id' field)
    updates = [
        {"id": "prod_123", "name": "Updated Product 1", "price": 19.99},
        {"id": "prod_456", "name": "Updated Product 2", "price": 29.99},
        {"id": "prod_789", "name": "Updated Product 3", "price": 39.99},
    ]

    print("Updating products in batch...")

    results = batch_ops.update_multiple(
        client.products,
        updates,
        batch_size=10,
    )

    print(f"Updated {len([r for r in results if r])} products")

    client.close()


def example_batch_delete():
    """Example: Delete multiple products in batches."""
    client = DistruClient(api_token="your_api_token")
    batch_ops = BatchOperations(client)

    # Product IDs to delete
    product_ids = ["prod_123", "prod_456", "prod_789"]

    print("Deleting products in batch...")

    results = batch_ops.delete_multiple(
        client.products,
        product_ids,
        batch_size=10,
    )

    successful_deletes = sum(results)
    print(f"Successfully deleted {successful_deletes} products")

    client.close()


def example_batch_fetch():
    """Example: Fetch multiple products by ID in batches."""
    client = DistruClient(api_token="your_api_token")
    batch_ops = BatchOperations(client)

    # Product IDs to fetch
    product_ids = [f"prod_{i}" for i in range(1, 21)]  # 20 IDs

    print("Fetching products by ID in batches...")

    products = batch_ops.fetch_by_ids(
        client.products,
        product_ids,
        batch_size=5,
        raise_on_error=False,
    )

    found = [p for p in products if p is not None]
    print(f"Found {len(found)} out of {len(product_ids)} products")

    client.close()


def example_custom_batch_processor():
    """Example: Custom batch processing with error handling."""
    client = DistruClient(api_token="your_api_token")

    # Custom error handler
    errors = []

    def on_error(item, error):
        """Called when an item fails to process."""
        errors.append({"item": item, "error": str(error)})
        print(f"Error processing {item.get('name')}: {error}")

    # Create custom processor
    processor = BatchProcessor(
        processor=client.products.create,
        batch_size=5,
        on_error=on_error,
    )

    # Process items
    products = [
        {"name": "Valid Product", "sku": "SKU-001"},
        {"name": "Another Valid", "sku": "SKU-002"},
        # This might fail if validation is strict
        {"invalid": "data"},
    ]

    results = processor.process(products, raise_on_error=False)

    print(f"Processed {len(results)} items")
    print(f"Errors encountered: {len(errors)}")

    client.close()


def example_bulk_iterator():
    """Example: Process paginated results in bulk batches."""
    client = DistruClient(api_token="your_api_token")

    print("Fetching all products and processing in batches of 50...")

    # Get paginated response
    response = client.products.list()

    # Process in bulk batches
    batch_count = 0
    total_count = 0

    for batch in BulkIterator(response.auto_paginate(), batch_size=50):
        batch_count += 1
        total_count += len(batch)

        print(f"Batch {batch_count}: Processing {len(batch)} products")

        # Process batch (e.g., save to database, export, etc.)
        for product in batch:
            # Do something with each product
            pass

    print(f"Processed {total_count} products in {batch_count} batches")

    client.close()


def example_parallel_batch_processing():
    """Example: Process multiple resources in parallel batches."""
    from concurrent.futures import ThreadPoolExecutor
    from distru_sdk.batch import BatchOperations

    client = DistruClient(api_token="your_api_token")
    batch_ops = BatchOperations(client)

    # Data for different resources
    products_data = [{"name": f"Product {i}", "sku": f"SKU-{i}"} for i in range(10)]
    contacts_data = [{"name": f"Contact {i}", "email": f"contact{i}@example.com"} for i in range(10)]

    def create_products():
        return batch_ops.create_multiple(client.products, products_data, batch_size=5)

    def create_contacts():
        return batch_ops.create_multiple(client.contacts, contacts_data, batch_size=5)

    print("Creating products and contacts in parallel...")

    # Execute in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        product_future = executor.submit(create_products)
        contact_future = executor.submit(create_contacts)

        products = product_future.result()
        contacts = contact_future.result()

    print(f"Created {len([p for p in products if p])} products")
    print(f"Created {len([c for c in contacts if c])} contacts")

    client.close()


def example_conditional_batch_processing():
    """Example: Conditionally process items in batches."""
    client = DistruClient(api_token="your_api_token")

    # Fetch all products
    response = client.products.list()

    # Filter and process in batches
    low_stock_products = []
    updates = []

    for product in response.auto_paginate():
        # Check condition (example: low stock)
        if hasattr(product, "quantity") and product.quantity < 10:
            low_stock_products.append(product)

            # Prepare update to reorder
            updates.append({
                "id": product.id,
                "status": "reorder_needed",
            })

    print(f"Found {len(low_stock_products)} low stock products")

    if updates:
        batch_ops = BatchOperations(client)
        results = batch_ops.update_multiple(
            client.products,
            updates,
            batch_size=10,
        )
        print(f"Updated {len([r for r in results if r])} products")

    client.close()


def example_batch_with_rate_limiting():
    """Example: Batch processing with manual rate limiting."""
    import time
    from distru_sdk.batch import BatchProcessor

    client = DistruClient(api_token="your_api_token")

    # Custom processor with rate limiting
    def rate_limited_create(product_data):
        """Create product with rate limiting."""
        result = client.products.create(product_data)
        time.sleep(0.1)  # 100ms delay between requests
        return result

    processor = BatchProcessor(
        processor=rate_limited_create,
        batch_size=5,
    )

    products = [
        {"name": f"Product {i}", "sku": f"SKU-{i:04d}"}
        for i in range(20)
    ]

    print("Creating products with rate limiting...")
    start = time.time()

    results = processor.process(products)

    elapsed = time.time() - start
    print(f"Created {len([r for r in results if r])} products in {elapsed:.2f}s")

    client.close()


if __name__ == "__main__":
    print("Batch Operations Examples\n")

    # Run examples (comment out what you don't need)
    # example_basic_batch_create()
    # example_batch_update()
    # example_batch_delete()
    # example_batch_fetch()
    # example_custom_batch_processor()
    # example_bulk_iterator()
    # example_parallel_batch_processing()
    # example_conditional_batch_processing()
    # example_batch_with_rate_limiting()

    print("\nDone!")
