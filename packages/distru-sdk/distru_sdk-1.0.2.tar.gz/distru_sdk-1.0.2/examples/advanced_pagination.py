"""Advanced pagination examples for Distru SDK.

This example demonstrates various pagination patterns and techniques.
"""

from distru_sdk import DistruClient
from distru_sdk.batch import BulkIterator


def example_basic_auto_pagination():
    """Example: Basic auto-pagination through all results."""
    client = DistruClient(api_token="your_api_token")

    print("Fetching all products with auto-pagination...")

    # Get first page
    response = client.products.list()

    # Auto-paginate through all pages
    count = 0
    for product in response.auto_paginate():
        count += 1
        print(f"{count}. {product.name} ({product.sku})")

    print(f"Total products: {count}")

    client.close()


def example_manual_pagination():
    """Example: Manual pagination with explicit page control."""
    client = DistruClient(api_token="your_api_token")

    print("Manual pagination through products...")

    page = 1
    total_count = 0

    while True:
        # Fetch specific page
        response = client.products.list(page=page, limit=20)

        print(f"\nPage {page}: {len(response.data)} products")

        for product in response:
            total_count += 1
            print(f"  - {product.name}")

        # Check if more pages exist
        if not response.has_more():
            break

        page += 1

    print(f"\nTotal products: {total_count}")

    client.close()


def example_page_iteration():
    """Example: Iterate through pages (not individual items)."""
    client = DistruClient(api_token="your_api_token")

    print("Iterating through pages...")

    response = client.products.list(limit=10)
    page_num = 1

    for page in response.iter_pages():
        print(f"\nPage {page_num}:")
        print(f"  Items in page: {len(page)}")
        print(f"  Has more: {page.has_more()}")

        # Process page
        for product in page:
            print(f"  - {product.name}")

        page_num += 1

    client.close()


def example_limited_pagination():
    """Example: Paginate with a limit on total items."""
    client = DistruClient(api_token="your_api_token")

    max_items = 50
    count = 0

    print(f"Fetching up to {max_items} products...")

    response = client.products.list()

    for product in response.auto_paginate():
        count += 1
        print(f"{count}. {product.name}")

        if count >= max_items:
            break

    print(f"Fetched {count} products")

    client.close()


def example_bulk_batch_pagination():
    """Example: Process paginated results in bulk batches."""
    client = DistruClient(api_token="your_api_token")

    print("Processing products in bulk batches...")

    response = client.products.list()
    batch_num = 1

    # Process in batches of 50
    for batch in BulkIterator(response.auto_paginate(), batch_size=50):
        print(f"\nBatch {batch_num}: {len(batch)} products")

        # Process batch (e.g., bulk insert to database)
        for product in batch:
            # Do something with product
            pass

        batch_num += 1

    client.close()


def example_filtered_pagination():
    """Example: Paginate with filtering and transformation."""
    client = DistruClient(api_token="your_api_token")

    print("Fetching and filtering products...")

    response = client.products.list()

    # Filter for products over $50
    expensive_products = []

    for product in response.auto_paginate():
        if hasattr(product, "price") and product.price > 50:
            expensive_products.append({
                "id": product.id,
                "name": product.name,
                "price": product.price,
            })

    print(f"Found {len(expensive_products)} products over $50")

    for p in expensive_products[:10]:  # Show first 10
        print(f"  - {p['name']}: ${p['price']}")

    client.close()


def example_concurrent_pagination():
    """Example: Fetch multiple pages concurrently."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    client = DistruClient(api_token="your_api_token")

    def fetch_page(page_num):
        """Fetch a specific page."""
        response = client.products.list(page=page_num, limit=20)
        return page_num, response.data

    print("Fetching pages concurrently...")

    # Fetch first 5 pages in parallel
    pages_to_fetch = range(1, 6)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_page, p): p for p in pages_to_fetch}

        results = {}
        for future in as_completed(futures):
            page_num, products = future.result()
            results[page_num] = products
            print(f"Page {page_num}: {len(products)} products")

    # Process in order
    all_products = []
    for page_num in sorted(results.keys()):
        all_products.extend(results[page_num])

    print(f"Total products fetched: {len(all_products)}")

    client.close()


def example_cursor_based_pagination():
    """Example: Cursor-based pagination (if supported by API)."""
    client = DistruClient(api_token="your_api_token")

    print("Cursor-based pagination...")

    # Note: This is conceptual - actual implementation depends on API support
    cursor = None
    count = 0

    while True:
        # Fetch with cursor
        params = {"limit": 20}
        if cursor:
            params["cursor"] = cursor

        response = client.products.list(**params)

        for product in response:
            count += 1
            print(f"{count}. {product.name}")

        # Get next cursor from response
        cursor = response.next_page

        if not cursor:
            break

    print(f"Total products: {count}")

    client.close()


def example_smart_pagination_with_caching():
    """Example: Smart pagination with result caching."""
    from distru_sdk.caching import InMemoryCache

    client = DistruClient(api_token="your_api_token")
    cache = InMemoryCache(default_ttl=300)

    def get_products_page(page, limit=20):
        """Get products page with caching."""
        cache_key = f"products_page_{page}_{limit}"

        # Check cache
        cached = cache.get(cache_key)
        if cached:
            print(f"  (from cache) Page {page}")
            return cached

        # Fetch from API
        print(f"  (from API) Page {page}")
        response = client.products.list(page=page, limit=limit)

        # Cache result
        cache.set(cache_key, response.data)

        return response.data

    print("Smart pagination with caching...")

    # First iteration - fetches from API
    print("\nFirst iteration:")
    for page in range(1, 4):
        products = get_products_page(page)
        print(f"  Page {page}: {len(products)} products")

    # Second iteration - uses cache
    print("\nSecond iteration (cached):")
    for page in range(1, 4):
        products = get_products_page(page)
        print(f"  Page {page}: {len(products)} products")

    client.close()


def example_progress_tracking_pagination():
    """Example: Track pagination progress."""
    from tqdm import tqdm

    client = DistruClient(api_token="your_api_token")

    # Get first page to estimate total (if API provides total count)
    first_response = client.products.list(limit=100)

    # Estimate total (you might get this from API response)
    # For demo, we'll process what we can get
    print("Fetching products with progress tracking...")

    # Create progress bar (unknown total)
    with tqdm(desc="Fetching products", unit="product") as pbar:
        for product in first_response.auto_paginate():
            # Process product
            pbar.update(1)

    print("Done!")

    client.close()


def example_rate_limited_pagination():
    """Example: Pagination with rate limiting."""
    import time

    client = DistruClient(api_token="your_api_token")

    print("Rate-limited pagination (max 2 pages/second)...")

    response = client.products.list()
    page_count = 0
    start_time = time.time()

    for page in response.iter_pages():
        page_count += 1
        print(f"Page {page_count}: {len(page)} products")

        # Rate limit: wait to achieve max 2 pages/second
        elapsed = time.time() - start_time
        expected_time = page_count * 0.5  # 0.5 seconds per page
        if elapsed < expected_time:
            time.sleep(expected_time - elapsed)

    total_time = time.time() - start_time
    print(f"Processed {page_count} pages in {total_time:.2f} seconds")

    client.close()


def example_aggregated_pagination():
    """Example: Aggregate data across all pages."""
    from collections import Counter

    client = DistruClient(api_token="your_api_token")

    print("Aggregating data across all pages...")

    response = client.products.list()

    # Aggregate statistics
    total_count = 0
    total_value = 0.0
    category_counts = Counter()

    for product in response.auto_paginate():
        total_count += 1

        if hasattr(product, "price"):
            total_value += float(product.price)

        if hasattr(product, "category"):
            category_counts[product.category] += 1

    print(f"\nAggregated Statistics:")
    print(f"  Total products: {total_count}")
    print(f"  Total value: ${total_value:,.2f}")
    print(f"  Average price: ${total_value/total_count:,.2f}" if total_count > 0 else "  Average price: N/A")
    print(f"\nTop categories:")
    for category, count in category_counts.most_common(5):
        print(f"  - {category}: {count}")

    client.close()


if __name__ == "__main__":
    print("Advanced Pagination Examples\n")

    # Run examples (comment out what you don't need)
    # example_basic_auto_pagination()
    # example_manual_pagination()
    # example_page_iteration()
    # example_limited_pagination()
    # example_bulk_batch_pagination()
    # example_filtered_pagination()
    # example_concurrent_pagination()
    # example_cursor_based_pagination()
    # example_smart_pagination_with_caching()
    # example_progress_tracking_pagination()
    # example_rate_limited_pagination()
    # example_aggregated_pagination()

    print("\nDone!")
