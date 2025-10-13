"""Flask integration example for Distru SDK.

This example shows how to integrate the Distru SDK with a Flask application.
"""

import os
from functools import wraps

from flask import Flask, jsonify, request, g
from flask_caching import Cache

from distru_sdk import DistruClient
from distru_sdk.batch import BatchOperations
from distru_sdk.exceptions import (
    DistruAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["DISTRU_API_TOKEN"] = os.getenv("DISTRU_API_TOKEN")
app.config["DISTRU_API_BASE_URL"] = os.getenv(
    "DISTRU_API_BASE_URL",
    "https://app.distru.com/public/v1"
)
app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

# Initialize cache
cache = Cache(app)


def get_distru_client() -> DistruClient:
    """Get or create Distru client for request context.

    Uses Flask's g object to store client per request.
    """
    if "distru_client" not in g:
        g.distru_client = DistruClient(
            api_token=app.config["DISTRU_API_TOKEN"],
            base_url=app.config["DISTRU_API_BASE_URL"],
        )
    return g.distru_client


@app.teardown_appcontext
def teardown_distru_client(error=None):
    """Close Distru client at end of request."""
    client = g.pop("distru_client", None)
    if client is not None:
        client.close()


def handle_distru_errors(f):
    """Decorator to handle Distru API errors.

    Converts Distru exceptions to appropriate JSON responses.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AuthenticationError as e:
            return jsonify({"error": str(e)}), 401
        except AuthorizationError as e:
            return jsonify({"error": str(e)}), 403
        except NotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except ValidationError as e:
            return jsonify({
                "error": str(e),
                "details": e.details
            }), 422
        except RateLimitError as e:
            response = jsonify({"error": str(e)})
            if e.retry_after:
                response.headers["Retry-After"] = str(e.retry_after)
            return response, 429
        except DistruAPIError as e:
            return jsonify({
                "error": str(e),
                "details": e.response_data
            }), e.status_code or 500
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500

    return decorated_function


# Product endpoints
@app.route("/api/products", methods=["GET"])
@handle_distru_errors
@cache.cached(timeout=300, query_string=True)
def list_products():
    """List products with caching."""
    client = get_distru_client()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    response = client.products.list(page=page, limit=limit)

    products = [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "price": str(getattr(p, "price", 0)),
        }
        for p in response.data
    ]

    return jsonify({
        "products": products,
        "next_page": response.next_page,
        "has_more": response.has_more(),
    })


@app.route("/api/products/<product_id>", methods=["GET"])
@handle_distru_errors
@cache.cached(timeout=300)
def get_product(product_id):
    """Get product by ID with caching."""
    client = get_distru_client()

    product = client.products.get(product_id)

    return jsonify({
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "description": getattr(product, "description", ""),
        "price": str(getattr(product, "price", 0)),
    })


@app.route("/api/products", methods=["POST"])
@handle_distru_errors
def create_product():
    """Create a new product."""
    client = get_distru_client()

    data = request.get_json()
    product = client.products.create(data)

    # Invalidate list cache
    cache.delete_memoized(list_products)

    return jsonify({
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
    }), 201


@app.route("/api/products/<product_id>", methods=["PATCH"])
@handle_distru_errors
def update_product(product_id):
    """Update a product."""
    client = get_distru_client()

    data = request.get_json()
    product = client.products.update(product_id, data)

    # Invalidate caches
    cache.delete_memoized(get_product, product_id)
    cache.delete_memoized(list_products)

    return jsonify({
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
    })


@app.route("/api/products/<product_id>", methods=["DELETE"])
@handle_distru_errors
def delete_product(product_id):
    """Delete a product."""
    client = get_distru_client()

    client.products.delete(product_id)

    # Invalidate caches
    cache.delete_memoized(get_product, product_id)
    cache.delete_memoized(list_products)

    return "", 204


# Batch operations endpoint
@app.route("/api/products/batch", methods=["POST"])
@handle_distru_errors
def batch_create_products():
    """Create multiple products in batch."""
    client = get_distru_client()
    batch_ops = BatchOperations(client)

    data = request.get_json()
    products = data.get("products", [])

    if not products:
        return jsonify({"error": "No products provided"}), 400

    # Create products in batches
    results = batch_ops.create_multiple(
        client.products,
        products,
        batch_size=10,
        raise_on_error=False,
    )

    # Count successes and failures
    successes = [r for r in results if r is not None]
    failures = len(results) - len(successes)

    # Invalidate cache
    cache.delete_memoized(list_products)

    return jsonify({
        "created": len(successes),
        "failed": failures,
        "products": [
            {"id": p.id, "name": p.name, "sku": p.sku}
            for p in successes
        ],
    }), 201


# Order endpoints
@app.route("/api/orders", methods=["GET"])
@handle_distru_errors
def list_orders():
    """List orders."""
    client = get_distru_client()

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    response = client.orders.list(page=page, limit=limit)

    orders = [
        {
            "id": o.id,
            "status": getattr(o, "status", "pending"),
            "total": str(getattr(o, "total", 0)),
            "created_at": str(getattr(o, "created_at", "")),
        }
        for o in response.data
    ]

    return jsonify({
        "orders": orders,
        "next_page": response.next_page,
        "has_more": response.has_more(),
    })


@app.route("/api/orders", methods=["POST"])
@handle_distru_errors
def create_order():
    """Create a new order."""
    client = get_distru_client()

    data = request.get_json()
    order = client.orders.create(data)

    return jsonify({
        "id": order.id,
        "status": getattr(order, "status", "pending"),
        "created_at": str(getattr(order, "created_at", "")),
    }), 201


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


# CLI command for syncing products
@app.cli.command("sync-products")
def sync_products():
    """Sync products from Distru API."""
    from distru_sdk.batch import BulkIterator

    client = DistruClient(
        api_token=app.config["DISTRU_API_TOKEN"],
        base_url=app.config["DISTRU_API_BASE_URL"],
    )

    print("Fetching products from Distru API...")

    response = client.products.list()
    count = 0

    # Process in bulk batches
    for batch in BulkIterator(response.auto_paginate(), batch_size=50):
        for product in batch:
            # Here you would save to database or process
            print(f"Processing: {product.name} ({product.sku})")
            count += 1

    print(f"Processed {count} products")
    client.close()


if __name__ == "__main__":
    app.run(debug=True)
