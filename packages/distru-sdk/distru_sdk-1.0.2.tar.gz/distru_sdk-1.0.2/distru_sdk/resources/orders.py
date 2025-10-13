"""Orders resource for managing sales orders."""

from typing import Any, Dict, List, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class OrdersResource(BaseResource):
    """Resource for managing orders in the Distru API.

    Orders represent sales transactions with customers, containing order items,
    pricing, and fulfillment information.

    Example:
        >>> orders = client.orders.list()
        >>> for order in orders.auto_paginate():
        ...     print(f"Order {order['order_number']} - {order['status']}")

        >>> order = client.orders.create(
        ...     company_relationship_id=123,
        ...     order_date="2025-10-06",
        ...     order_items=[
        ...         {
        ...             "product_id": "prod-uuid-123",
        ...             "quantity": 10,
        ...             "unit_price": "15.00"
        ...         }
        ...     ]
        ... )
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        company_relationship_id: Optional[int] = None,
        status: Optional[str] = None,
        order_date_start: Optional[str] = None,
        order_date_end: Optional[str] = None,
        order_number: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all orders.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            company_relationship_id: Filter by customer company relationship ID
            status: Filter by order status (e.g., "pending", "approved", "fulfilled")
            order_date_start: Filter by order date start (ISO format)
            order_date_end: Filter by order date end (ISO format)
            order_number: Filter by order number
            **params: Additional query parameters

        Returns:
            Paginated list of orders

        Example:
            >>> # Get all orders
            >>> orders = client.orders.list()
            >>>
            >>> # Filter by customer
            >>> orders = client.orders.list(company_relationship_id=123)
            >>>
            >>> # Filter by status
            >>> orders = client.orders.list(status="approved")
            >>>
            >>> # Filter by date range
            >>> orders = client.orders.list(
            ...     order_date_start="2025-01-01",
            ...     order_date_end="2025-12-31"
            ... )
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if company_relationship_id is not None:
            query_params["company_relationship_id"] = company_relationship_id
        if status is not None:
            query_params["status"] = status
        if order_date_start is not None:
            query_params["order_date_start"] = order_date_start
        if order_date_end is not None:
            query_params["order_date_end"] = order_date_end
        if order_number is not None:
            query_params["order_number"] = order_number

        response_data = self._get("/orders", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, order_id: str) -> Dict[str, Any]:
        """Get a specific order by ID.

        Args:
            order_id: Order UUID

        Returns:
            Order data with line items and related information

        Raises:
            NotFoundError: If order not found

        Example:
            >>> order = client.orders.get("order-uuid-123")
            >>> print(f"Order {order['order_number']} total: {order['total']}")
        """
        return self._get(f"/orders/{order_id}")

    def create(
        self,
        company_relationship_id: int,
        order_date: str,
        order_items: List[Dict[str, Any]],
        order_number: Optional[str] = None,
        status: Optional[str] = None,
        ship_date: Optional[str] = None,
        delivery_date: Optional[str] = None,
        notes: Optional[str] = None,
        invoice_notes: Optional[str] = None,
        payment_term_id: Optional[int] = None,
        location_id: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new order.

        Args:
            company_relationship_id: Customer company relationship ID (required)
            order_date: Order date in ISO format (required)
            order_items: List of order items (required), each containing:
                - product_id: Product UUID
                - quantity: Quantity ordered
                - unit_price: Price per unit
                - batch_id: (optional) Batch UUID for batch-tracked products
                - package_id: (optional) Package UUID for package-tracked products
            order_number: Order number (auto-generated if not provided)
            status: Order status
            ship_date: Expected ship date
            delivery_date: Expected delivery date
            notes: Internal notes
            invoice_notes: Notes to appear on invoice
            payment_term_id: Payment terms ID
            location_id: Location ID
            custom_data: Custom data dictionary
            **kwargs: Additional order fields

        Returns:
            Created order data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> order = client.orders.create(
            ...     company_relationship_id=123,
            ...     order_date="2025-10-06",
            ...     order_items=[
            ...         {
            ...             "product_id": "prod-uuid-123",
            ...             "quantity": 10,
            ...             "unit_price": "15.00"
            ...         },
            ...         {
            ...             "product_id": "prod-uuid-456",
            ...             "quantity": 5,
            ...             "unit_price": "25.00"
            ...         }
            ...     ],
            ...     notes="Rush order"
            ... )
        """
        order_data: Dict[str, Any] = {
            "company_relationship_id": company_relationship_id,
            "order_date": order_date,
            "order_items": order_items,
            **kwargs,
        }

        if order_number is not None:
            order_data["order_number"] = order_number
        if status is not None:
            order_data["status"] = status
        if ship_date is not None:
            order_data["ship_date"] = ship_date
        if delivery_date is not None:
            order_data["delivery_date"] = delivery_date
        if notes is not None:
            order_data["notes"] = notes
        if invoice_notes is not None:
            order_data["invoice_notes"] = invoice_notes
        if payment_term_id is not None:
            order_data["payment_term_id"] = payment_term_id
        if location_id is not None:
            order_data["location_id"] = location_id
        if custom_data is not None:
            order_data["custom_data"] = custom_data

        # Ensure 'id' is not in order_data (create always generates new ID)
        order_data.pop('id', None)

        return self._post("/orders", json={"order": order_data})

    def update(
        self,
        order_id: str,
        **changes: Any,
    ) -> Dict[str, Any]:
        """Update an existing order (smart merge).

        This method automatically fetches the current order state and merges
        your changes, preventing accidental deletion of items and charges.

        ⚠️ IMPORTANT: The API requires ALL fields when updating.
        This method fetches current data and merges to make updates safe.

        Args:
            order_id: Order UUID
            **changes: Fields to update (e.g., status="COMPLETED", notes="Done")

        Returns:
            Updated order data

        Raises:
            NotFoundError: If order not found
            ValidationError: If validation fails

        Example:
            >>> # Safe update - preserves items and charges
            >>> order = client.orders.update(
            ...     "order-uuid-123",
            ...     status="COMPLETED"
            ... )
            >>>
            >>> # Update multiple fields
            >>> order = client.orders.update(
            ...     "order-uuid-123",
            ...     status="PROCESSING",
            ...     notes="Rush order",
            ...     ship_date="2025-10-15"
            ... )
        """
        # Fetch current order state
        current = self.get(order_id)

        # Merge changes into current state
        merged_data = {**current, **changes}

        # If user didn't specify items, preserve existing
        if 'items' not in changes and 'order_items' not in changes:
            merged_data['items'] = current.get('items', current.get('order_items', []))

        # If user didn't specify charges, preserve existing
        if 'charges' not in changes and 'order_charges' not in changes:
            merged_data['charges'] = current.get('charges', current.get('order_charges', []))

        # Use upsert to update
        return self.upsert(merged_data, id=order_id)

    def upsert(
        self,
        data: Dict[str, Any],
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update an order.

        If id is provided and exists, updates that order.
        If id is provided but doesn't exist, creates a new order with that id.
        If id is not provided, creates a new order with auto-generated id.

        ⚠️ IMPORTANT: When updating via upsert, you must provide ALL fields.
        The API uses full replacement (non-sparse updates).
        Any items/charges not included will be DELETED.

        For safe updates that preserve items/charges, use update() instead.

        Args:
            data: Complete order data dictionary
            id: Optional order UUID for upsert behavior

        Returns:
            Created or updated order data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> # Create with auto-generated ID
            >>> order = client.orders.upsert({
            ...     "company_id": "...",
            ...     "items": [{"product_id": "...", "quantity": 10}]
            ... })
            >>>
            >>> # Create with specific ID (idempotent - great for integrations)
            >>> order = client.orders.upsert(
            ...     {"company_id": "...", "items": [...]},
            ...     id="my-external-system-id"
            ... )
            >>>
            >>> # Update existing (must provide ALL fields!)
            >>> order = client.orders.upsert(
            ...     {
            ...         "company_id": "...",
            ...         "items": [...],  # All items
            ...         "charges": [...],  # All charges
            ...         # ... all other fields ...
            ...     },
            ...     id="existing-order-uuid"
            ... )
        """
        params = {}
        if id is not None:
            params["id"] = id

        return self._post("/orders", params=params, json={"order": data})

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of orders."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
