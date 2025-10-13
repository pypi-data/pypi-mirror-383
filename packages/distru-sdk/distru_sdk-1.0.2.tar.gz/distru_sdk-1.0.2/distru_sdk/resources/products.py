"""Products resource for managing product catalog."""

from typing import Any, Dict, List, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class ProductsResource(BaseResource):
    """Resource for managing products in the Distru API.

    Products are items in your catalog that can be sold, purchased, or tracked
    in inventory.

    Example:
        >>> products = client.products.list()
        >>> for product in products.auto_paginate():
        ...     print(f"{product['name']} - {product['sku']}")

        >>> product = client.products.create(
        ...     name="Blue Dream 1g",
        ...     sku="BD-1G",
        ...     unit_type_id=1,
        ...     inventory_tracking_method="BATCH"
        ... )
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sku: Optional[str] = None,
        category_id: Optional[int] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all products.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            include_inactive: Include inactive products
            search: Search by product name or SKU
            sku: Filter by exact SKU
            category_id: Filter by category ID
            **params: Additional query parameters

        Returns:
            Paginated list of products

        Example:
            >>> # Get all products
            >>> products = client.products.list()
            >>>
            >>> # Search for products
            >>> products = client.products.list(search="Blue Dream")
            >>>
            >>> # Filter by category
            >>> products = client.products.list(category_id=5)
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if include_inactive is not None:
            query_params["include_inactive"] = include_inactive
        if search is not None:
            query_params["search"] = search
        if sku is not None:
            query_params["sku"] = sku
        if category_id is not None:
            query_params["category_id"] = category_id

        response_data = self._get("/products", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )


    def create(
        self,
        name: str,
        unit_type_id: int,
        inventory_tracking_method: str,
        sku: Optional[str] = None,
        description: Optional[str] = None,
        description_markdown: Optional[str] = None,
        category_id: Optional[int] = None,
        subcategory_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        company_relationship_id: Optional[int] = None,
        sale_price: Optional[str] = None,
        wholesale_price: Optional[str] = None,
        unit_cost: Optional[str] = None,
        net_weight: Optional[str] = None,
        thc: Optional[str] = None,
        cbd: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new product.

        Args:
            name: Product name (required, max 250 chars)
            unit_type_id: Unit type ID (required)
            inventory_tracking_method: One of: "BATCH", "PACKAGE", "NONE" (required)
            sku: Stock keeping unit (SKU)
            description: Product description
            description_markdown: Product description in markdown format
            category_id: Category ID
            subcategory_id: Subcategory ID
            brand_id: Brand company relationship ID
            company_relationship_id: Vendor company relationship ID
            sale_price: Retail sale price
            wholesale_price: Wholesale price
            unit_cost: Cost per unit
            net_weight: Net weight
            thc: THC content
            cbd: CBD content
            custom_data: Custom data dictionary
            **kwargs: Additional product fields

        Returns:
            Created product data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> product = client.products.create(
            ...     name="Blue Dream 1g",
            ...     sku="BD-1G",
            ...     unit_type_id=1,
            ...     inventory_tracking_method="BATCH",
            ...     sale_price="15.00",
            ...     wholesale_price="10.00"
            ... )
        """
        product_data: Dict[str, Any] = {
            "name": name,
            "unit_type_id": unit_type_id,
            "inventory_tracking_method": inventory_tracking_method,
            **kwargs,
        }

        if sku is not None:
            product_data["sku"] = sku
        if description is not None:
            product_data["description"] = description
        if description_markdown is not None:
            product_data["description_markdown"] = description_markdown
        if category_id is not None:
            product_data["category_id"] = category_id
        if subcategory_id is not None:
            product_data["subcategory_id"] = subcategory_id
        if brand_id is not None:
            product_data["brand_id"] = brand_id
        if company_relationship_id is not None:
            product_data["company_relationship_id"] = company_relationship_id
        if sale_price is not None:
            product_data["sale_price"] = sale_price
        if wholesale_price is not None:
            product_data["wholesale_price"] = wholesale_price
        if unit_cost is not None:
            product_data["unit_cost"] = unit_cost
        if net_weight is not None:
            product_data["net_weight"] = net_weight
        if thc is not None:
            product_data["thc"] = thc
        if cbd is not None:
            product_data["cbd"] = cbd
        if custom_data is not None:
            product_data["custom_data"] = custom_data

        # Ensure 'id' is not in product_data (create always generates new ID)
        product_data.pop('id', None)

        return self._post("/products", json={"product": product_data})

    def upsert(
        self,
        data: Dict[str, Any],
        id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update a product.

        If id is provided and exists, updates that product.
        If id is provided but doesn't exist, creates a new product with that id.
        If id is not provided, creates a new product with auto-generated id.

        ⚠️ IMPORTANT: When updating, you must provide ALL fields.
        The API uses full replacement (non-sparse updates).
        Any fields not included will be set to null or default values.

        Args:
            data: Complete product data dictionary
            id: Optional product UUID for upsert behavior

        Returns:
            Created or updated product data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> # Create with auto-generated ID
            >>> product = client.products.upsert({
            ...     "name": "Blue Dream 1g",
            ...     "sku": "BD-1G",
            ...     "unit_type_id": 1,
            ...     "inventory_tracking_method": "BATCH"
            ... })
            >>>
            >>> # Create with specific ID (idempotent)
            >>> product = client.products.upsert(
            ...     {"name": "Blue Dream 1g", "sku": "BD-1G", ...},
            ...     id="my-custom-uuid"
            ... )
            >>>
            >>> # Update existing (must provide ALL fields!)
            >>> product = client.products.upsert(
            ...     {
            ...         "name": "Blue Dream 1g UPDATED",
            ...         "sku": "BD-1G",
            ...         "unit_type_id": 1,
            ...         "inventory_tracking_method": "BATCH",
            ...         # ... all other fields required ...
            ...     },
            ...     id="existing-product-uuid"
            ... )
        """
        params = {}
        if id is not None:
            params["id"] = id

        return self._post("/products", params=params, json={"product": data})

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of products."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
