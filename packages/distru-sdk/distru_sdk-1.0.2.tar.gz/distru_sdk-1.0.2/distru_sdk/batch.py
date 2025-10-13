"""Batch operations helper for Distru SDK.

Provides utilities for efficiently processing multiple operations.
"""

from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class BatchProcessor(Generic[T, R]):
    """Process items in batches with configurable batch size.

    Example:
        >>> def process_item(item):
        ...     return client.products.create(item)
        >>> processor = BatchProcessor(process_item, batch_size=10)
        >>> results = processor.process(items)
    """

    def __init__(
        self,
        processor: Callable[[T], R],
        batch_size: int = 10,
        on_error: Optional[Callable[[T, Exception], None]] = None,
    ) -> None:
        """Initialize batch processor.

        Args:
            processor: Function to process each item
            batch_size: Number of items to process in each batch
            on_error: Optional callback for handling errors (item, error)
        """
        self.processor = processor
        self.batch_size = batch_size
        self.on_error = on_error

    def process(
        self,
        items: Iterable[T],
        raise_on_error: bool = False,
    ) -> List[R]:
        """Process items in batches.

        Args:
            items: Items to process
            raise_on_error: If True, raise first error encountered

        Returns:
            List of results (may have None for failed items)

        Raises:
            Exception: If raise_on_error=True and an error occurs
        """
        results: List[Optional[R]] = []
        batch: List[T] = []

        for item in items:
            batch.append(item)

            if len(batch) >= self.batch_size:
                results.extend(self._process_batch(batch, raise_on_error))
                batch = []

        # Process remaining items
        if batch:
            results.extend(self._process_batch(batch, raise_on_error))

        return results  # type: ignore

    def _process_batch(
        self,
        batch: List[T],
        raise_on_error: bool,
    ) -> List[Optional[R]]:
        """Process a single batch of items.

        Args:
            batch: Batch of items
            raise_on_error: If True, raise on error

        Returns:
            List of results

        Raises:
            Exception: If raise_on_error=True and an error occurs
        """
        results: List[Optional[R]] = []

        for item in batch:
            try:
                result = self.processor(item)
                results.append(result)
            except Exception as e:
                if raise_on_error:
                    raise
                if self.on_error:
                    self.on_error(item, e)
                results.append(None)

        return results


class BatchOperations:
    """Helper methods for common batch operations.

    Example:
        >>> batch_ops = BatchOperations(client)
        >>> results = batch_ops.create_multiple(
        ...     client.products,
        ...     [{"name": "Product 1"}, {"name": "Product 2"}]
        ... )
    """

    def __init__(self, client: Any) -> None:
        """Initialize batch operations helper.

        Args:
            client: DistruClient instance
        """
        self.client = client

    def create_multiple(
        self,
        resource: Any,
        items: List[Dict[str, Any]],
        batch_size: int = 10,
        raise_on_error: bool = False,
    ) -> List[Any]:
        """Create multiple items in batches.

        Args:
            resource: Resource endpoint (e.g., client.products)
            items: List of item data dictionaries
            batch_size: Number of items per batch
            raise_on_error: If True, stop on first error

        Returns:
            List of created items

        Example:
            >>> items = [
            ...     {"name": "Product 1", "sku": "SKU-001"},
            ...     {"name": "Product 2", "sku": "SKU-002"},
            ... ]
            >>> results = batch_ops.create_multiple(client.products, items)
        """
        processor = BatchProcessor(
            processor=resource.create,
            batch_size=batch_size,
        )
        return processor.process(items, raise_on_error=raise_on_error)

    def update_multiple(
        self,
        resource: Any,
        updates: List[Dict[str, Any]],
        batch_size: int = 10,
        raise_on_error: bool = False,
    ) -> List[Any]:
        """Update multiple items in batches.

        Args:
            resource: Resource endpoint (e.g., client.products)
            updates: List of update dictionaries with 'id' and update fields
            batch_size: Number of items per batch
            raise_on_error: If True, stop on first error

        Returns:
            List of updated items

        Example:
            >>> updates = [
            ...     {"id": "123", "name": "Updated Product 1"},
            ...     {"id": "456", "name": "Updated Product 2"},
            ... ]
            >>> results = batch_ops.update_multiple(client.products, updates)
        """

        def update_item(update: Dict[str, Any]) -> Any:
            # Create a copy to avoid mutating caller's data
            update_copy = update.copy()
            item_id = update_copy.pop("id")
            return resource.update(item_id, update_copy)

        processor = BatchProcessor(
            processor=update_item,
            batch_size=batch_size,
        )
        return processor.process(updates, raise_on_error=raise_on_error)

    def delete_multiple(
        self,
        resource: Any,
        ids: List[str],
        batch_size: int = 10,
        raise_on_error: bool = False,
    ) -> List[bool]:
        """Delete multiple items in batches.

        Args:
            resource: Resource endpoint (e.g., client.products)
            ids: List of item IDs to delete
            batch_size: Number of items per batch
            raise_on_error: If True, stop on first error

        Returns:
            List of success flags (True if deleted, False if failed)

        Example:
            >>> ids = ["123", "456", "789"]
            >>> results = batch_ops.delete_multiple(client.products, ids)
        """

        def delete_item(item_id: str) -> bool:
            try:
                resource.delete(item_id)
                return True
            except Exception:
                return False

        processor = BatchProcessor(
            processor=delete_item,
            batch_size=batch_size,
        )
        return processor.process(ids, raise_on_error=raise_on_error)

    def fetch_by_ids(
        self,
        resource: Any,
        ids: List[str],
        batch_size: int = 10,
        raise_on_error: bool = False,
    ) -> List[Any]:
        """Fetch multiple items by ID in batches.

        Args:
            resource: Resource endpoint (e.g., client.products)
            ids: List of item IDs to fetch
            batch_size: Number of items per batch
            raise_on_error: If True, stop on first error

        Returns:
            List of items (None for items that couldn't be fetched)

        Example:
            >>> ids = ["123", "456", "789"]
            >>> items = batch_ops.fetch_by_ids(client.products, ids)
        """
        processor = BatchProcessor(
            processor=resource.get,
            batch_size=batch_size,
        )
        return processor.process(ids, raise_on_error=raise_on_error)


class BulkIterator(Generic[T]):
    """Iterator that yields items in bulk/batches.

    Useful for processing paginated results in controlled batches.

    Example:
        >>> response = client.products.list()
        >>> for batch in BulkIterator(response.auto_paginate(), batch_size=50):
        ...     process_batch(batch)
    """

    def __init__(self, iterable: Iterable[T], batch_size: int = 10) -> None:
        """Initialize bulk iterator.

        Args:
            iterable: Source iterable
            batch_size: Number of items per batch
        """
        self.iterable = iter(iterable)
        self.batch_size = batch_size

    def __iter__(self) -> "BulkIterator[T]":
        """Return iterator."""
        return self

    def __next__(self) -> List[T]:
        """Get next batch of items.

        Returns:
            List of items in next batch

        Raises:
            StopIteration: When no more items
        """
        batch: List[T] = []

        try:
            for _ in range(self.batch_size):
                batch.append(next(self.iterable))
        except StopIteration:
            if not batch:
                raise
            # Return partial batch if we have items

        return batch
