"""FastAPI integration example for Distru SDK.

This example shows how to integrate the Distru SDK with a FastAPI application,
including async support.
"""

import os
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from distru_sdk.async_client import AsyncDisruClient
from distru_sdk.exceptions import (
    DistruAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

# Pydantic models
class ProductCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: Optional[float] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    description: Optional[str] = None
    price: Optional[float] = None


class OrderCreate(BaseModel):
    contact_id: str
    items: List[dict]
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    status: str
    created_at: str


# Global client instance
distru_client: Optional[AsyncDisruClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app.

    Handles client initialization and cleanup.
    """
    global distru_client

    # Startup: Create client
    api_token = os.getenv("DISTRU_API_TOKEN")
    if not api_token:
        raise ValueError("DISTRU_API_TOKEN environment variable is required")

    distru_client = AsyncDisruClient(
        api_token=api_token,
        base_url=os.getenv("DISTRU_API_BASE_URL", "https://app.distru.com/public/v1"),
        timeout=float(os.getenv("DISTRU_API_TIMEOUT", "30.0")),
        max_retries=int(os.getenv("DISTRU_API_MAX_RETRIES", "3")),
    )

    yield

    # Shutdown: Close client
    if distru_client:
        await distru_client.close()


# Create FastAPI app
app = FastAPI(
    title="Distru API Integration",
    description="FastAPI integration with Distru SDK",
    version="1.0.0",
    lifespan=lifespan,
)


def get_client() -> AsyncDisruClient:
    """Dependency to get Distru client."""
    if distru_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Distru client not initialized"
        )
    return distru_client


async def handle_distru_error(error: DistruAPIError):
    """Convert Distru API errors to HTTP exceptions."""
    if isinstance(error, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(error))
    elif isinstance(error, AuthorizationError):
        raise HTTPException(status_code=403, detail=str(error))
    elif isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, ValidationError):
        raise HTTPException(
            status_code=422,
            detail={"message": str(error), "details": error.details}
        )
    elif isinstance(error, RateLimitError):
        headers = {}
        if error.retry_after:
            headers["Retry-After"] = str(error.retry_after)
        raise HTTPException(
            status_code=429,
            detail=str(error),
            headers=headers
        )
    else:
        raise HTTPException(
            status_code=error.status_code or 500,
            detail=str(error)
        )


# Product endpoints
@app.get("/api/products", response_model=dict)
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    client: AsyncDisruClient = Depends(get_client)
):
    """List products with pagination.

    Returns a paginated list of products from the Distru API.
    """
    try:
        # Note: This is a conceptual example
        # You'd need to implement async methods in resources
        # or use the sync client in a thread pool
        response = await client.request("GET", "/products", params={"page": page, "limit": limit})
        data = response.json()

        return {
            "products": data.get("data", []),
            "next_page": data.get("next_page"),
            "has_more": data.get("next_page") is not None,
        }
    except DistruAPIError as e:
        await handle_distru_error(e)


@app.get("/api/products/{product_id}", response_model=dict)
async def get_product(
    product_id: str,
    client: AsyncDisruClient = Depends(get_client)
):
    """Get product by ID."""
    try:
        response = await client.request("GET", f"/products/{product_id}")
        return response.json()
    except DistruAPIError as e:
        await handle_distru_error(e)


@app.post("/api/products", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    client: AsyncDisruClient = Depends(get_client)
):
    """Create a new product."""
    try:
        response = await client.request(
            "POST",
            "/products",
            json=product.dict(exclude_none=True)
        )
        return response.json()
    except DistruAPIError as e:
        await handle_distru_error(e)


@app.patch("/api/products/{product_id}", response_model=dict)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    client: AsyncDisruClient = Depends(get_client)
):
    """Update a product."""
    try:
        response = await client.request(
            "PATCH",
            f"/products/{product_id}",
            json=product.dict(exclude_none=True)
        )
        return response.json()
    except DistruAPIError as e:
        await handle_distru_error(e)


@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    client: AsyncDisruClient = Depends(get_client)
):
    """Delete a product."""
    try:
        await client.request("DELETE", f"/products/{product_id}")
        return None
    except DistruAPIError as e:
        await handle_distru_error(e)


# Batch operations endpoint
@app.post("/api/products/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def batch_create_products(
    products: List[ProductCreate],
    client: AsyncDisruClient = Depends(get_client)
):
    """Create multiple products in batch.

    This is a simplified example. For production, you'd want to:
    - Use asyncio.gather for parallel requests
    - Handle partial failures gracefully
    - Return detailed results for each product
    """
    import asyncio

    async def create_one(product_data: ProductCreate):
        try:
            response = await client.request(
                "POST",
                "/products",
                json=product_data.dict(exclude_none=True)
            )
            return response.json()
        except DistruAPIError:
            return None

    # Create all products concurrently
    results = await asyncio.gather(*[create_one(p) for p in products])

    successes = [r for r in results if r is not None]
    failures = len(results) - len(successes)

    return {
        "created": len(successes),
        "failed": failures,
        "products": successes,
    }


# Order endpoints
@app.get("/api/orders", response_model=dict)
async def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    client: AsyncDisruClient = Depends(get_client)
):
    """List orders with pagination."""
    try:
        response = await client.request("GET", "/orders", params={"page": page, "limit": limit})
        data = response.json()

        return {
            "orders": data.get("data", []),
            "next_page": data.get("next_page"),
            "has_more": data.get("next_page") is not None,
        }
    except DistruAPIError as e:
        await handle_distru_error(e)


@app.post("/api/orders", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    client: AsyncDisruClient = Depends(get_client)
):
    """Create a new order."""
    try:
        response = await client.request(
            "POST",
            "/orders",
            json=order.dict(exclude_none=True)
        )
        return response.json()
    except DistruAPIError as e:
        await handle_distru_error(e)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Background task example
from fastapi import BackgroundTasks


@app.post("/api/sync/products")
async def sync_products_background(
    background_tasks: BackgroundTasks,
    client: AsyncDisruClient = Depends(get_client)
):
    """Trigger background product sync."""

    async def sync_task():
        """Background task to sync products."""
        try:
            response = await client.request("GET", "/products", params={"limit": 100})
            data = response.json()

            products = data.get("data", [])
            # Process products (save to DB, etc.)
            print(f"Synced {len(products)} products")

        except DistruAPIError as e:
            print(f"Error syncing products: {e}")

    background_tasks.add_task(sync_task)

    return {"message": "Product sync started in background"}


# WebSocket example for real-time updates
from fastapi import WebSocket


@app.websocket("/ws/products")
async def websocket_products(websocket: WebSocket):
    """WebSocket endpoint for real-time product updates.

    This is a conceptual example showing how you might stream
    product updates to connected clients.
    """
    await websocket.accept()

    try:
        while True:
            # In a real implementation, you'd:
            # 1. Poll the API for changes
            # 2. Listen to webhooks
            # 3. Use a message queue

            # For demo purposes, just send periodic updates
            import asyncio
            await asyncio.sleep(5)

            response = await distru_client.request("GET", "/products", params={"limit": 5})
            data = response.json()

            await websocket.send_json({
                "type": "products_update",
                "products": data.get("data", [])
            })

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
