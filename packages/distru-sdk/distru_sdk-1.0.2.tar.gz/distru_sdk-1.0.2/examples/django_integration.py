"""Django integration example for Distru SDK.

This example shows how to integrate the Distru SDK with a Django application.
"""

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from functools import wraps
import logging

from distru_sdk import DistruClient
from distru_sdk.caching import CacheBackend, ResponseCache
from distru_sdk.exceptions import DistruAPIError

# Configure logging
logger = logging.getLogger(__name__)


# Custom Django cache backend for Distru SDK
class DjangoCacheBackend(CacheBackend):
    """Django cache backend for Distru SDK caching.

    Uses Django's cache framework for distributed caching.
    """

    def __init__(self, prefix: str = "distru:", default_ttl: int = 300):
        self.prefix = prefix
        self.default_ttl = default_ttl

    def _make_key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def get(self, key: str):
        return cache.get(self._make_key(key))

    def set(self, key: str, value, ttl: int = None):
        timeout = ttl if ttl is not None else self.default_ttl
        cache.set(self._make_key(key), value, timeout=timeout)

    def delete(self, key: str):
        cache.delete(self._make_key(key))

    def clear(self):
        # Django's cache.clear() clears all cache
        cache.clear()


# Singleton client instance
_client = None


def get_distru_client(use_cache: bool = True) -> DistruClient:
    """Get or create Distru API client instance.

    Args:
        use_cache: Whether to enable response caching

    Returns:
        DistruClient instance
    """
    global _client

    if _client is None:
        api_token = settings.DISTRU_API_TOKEN

        if use_cache:
            # Use Django cache for response caching
            cache_backend = DjangoCacheBackend(
                prefix="distru:",
                default_ttl=getattr(settings, "DISTRU_CACHE_TTL", 300)
            )
            response_cache = ResponseCache(backend=cache_backend)
            # Note: You'd need to extend DistruClient to support response_cache
            # This is a conceptual example

        _client = DistruClient(
            api_token=api_token,
            base_url=getattr(settings, "DISTRU_API_BASE_URL", None),
            timeout=getattr(settings, "DISTRU_API_TIMEOUT", 30.0),
            max_retries=getattr(settings, "DISTRU_API_MAX_RETRIES", 3),
        )

    return _client


def handle_distru_errors(view_func):
    """Decorator to handle Distru API errors in Django views.

    Converts Distru exceptions to appropriate HTTP responses.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except DistruAPIError as e:
            logger.error(f"Distru API error: {e}", exc_info=True)

            status_code = e.status_code or 500
            return JsonResponse({
                "error": str(e),
                "details": e.response_data
            }, status=status_code)
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return JsonResponse({
                "error": "Internal server error"
            }, status=500)

    return wrapper


# Example Django views
class ProductListView(View):
    """List products from Distru API."""

    @handle_distru_errors
    def get(self, request):
        client = get_distru_client()

        # Get query parameters
        page = request.GET.get("page", 1)
        limit = request.GET.get("limit", 20)

        # Fetch products
        response = client.products.list(page=page, limit=limit)

        # Serialize products
        products = [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "price": str(p.price) if hasattr(p, "price") else None,
            }
            for p in response.data
        ]

        return JsonResponse({
            "products": products,
            "next_page": response.next_page,
            "has_more": response.has_more(),
        })


class ProductDetailView(View):
    """Get product details from Distru API."""

    @handle_distru_errors
    def get(self, request, product_id):
        client = get_distru_client()

        # Fetch product
        product = client.products.get(product_id)

        return JsonResponse({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "description": getattr(product, "description", ""),
            "price": str(getattr(product, "price", 0)),
        })


class OrderCreateView(View):
    """Create order via Distru API."""

    @handle_distru_errors
    def post(self, request):
        client = get_distru_client()

        import json
        data = json.loads(request.body)

        # Create order
        order = client.orders.create(data)

        return JsonResponse({
            "id": order.id,
            "status": getattr(order, "status", "pending"),
            "created_at": str(getattr(order, "created_at", "")),
        }, status=201)


# Django management command example
from django.core.management.base import BaseCommand
from distru_sdk.batch import BatchOperations


class Command(BaseCommand):
    """Django management command to sync products from Distru."""

    help = "Sync products from Distru API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of products to process in each batch"
        )

    def handle(self, *args, **options):
        client = get_distru_client()
        batch_size = options["batch_size"]

        self.stdout.write("Fetching products from Distru API...")

        # Fetch all products with auto-pagination
        response = client.products.list()
        products = []

        for product in response.auto_paginate():
            products.append(product)

            # Process in batches
            if len(products) >= batch_size:
                self._sync_batch(products)
                products = []

        # Process remaining products
        if products:
            self._sync_batch(products)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully synced products")
        )

    def _sync_batch(self, products):
        """Sync a batch of products to database."""
        from myapp.models import Product  # Your Django model

        for product_data in products:
            Product.objects.update_or_create(
                distru_id=product_data.id,
                defaults={
                    "name": product_data.name,
                    "sku": product_data.sku,
                    "price": getattr(product_data, "price", 0),
                }
            )


# Settings example (settings.py)
"""
# Distru API Configuration
DISTRU_API_TOKEN = env("DISTRU_API_TOKEN")
DISTRU_API_BASE_URL = env("DISTRU_API_BASE_URL", default="https://app.distru.com/public/v1")
DISTRU_API_TIMEOUT = 30.0
DISTRU_API_MAX_RETRIES = 3
DISTRU_CACHE_TTL = 300  # 5 minutes

# URLs configuration (urls.py)
from django.urls import path
from .views import ProductListView, ProductDetailView, OrderCreateView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
]
"""
