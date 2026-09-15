import os
import json
import redis

from typing import List

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel


app = FastAPI(
    title="E-Commerce Cart Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# Models
class CartItem(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int


class AddToCartRequest(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int


class UpdateCartRequest(BaseModel):
    quantity: int


# Redis helpers
def get_cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


def load_cart(user_id: int) -> List[CartItem]:
    key = get_cart_key(user_id)

    data = redis_client.get(key)

    if not data:
        return []

    return [
        CartItem(**item)
        for item in json.loads(data)
    ]


def save_cart(
    user_id: int,
    items: List[CartItem]
):
    key = get_cart_key(user_id)

    data = [
        item.model_dump()
        for item in items
    ]

    redis_client.set(
        key,
        json.dumps(data)
    )


# Root endpoint
@app.get("/")
def root():
    return {
        "service": "cart-service",
        "status": "running"
    }


# Health check
@app.get("/health")
def health():
    try:
        redis_client.ping()

        return {
            "status": "healthy",
            "redis": "connected"
        }

    except redis.RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable"
        )


# Get user's cart
@app.get("/cart/{user_id}")
def get_cart(user_id: int):
    items = load_cart(user_id)

    total = sum(
        item.price * item.quantity
        for item in items
    )

    return {
        "user_id": user_id,
        "items": items,
        "total": total
    }


# Add item to cart
@app.post("/cart/{user_id}/items")
def add_to_cart(
    user_id: int,
    request: AddToCartRequest
):
    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    if request.price < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
        )

    items = load_cart(user_id)

    # Update quantity if product already exists
    for item in items:

        if item.product_id == request.product_id:

            item.quantity += request.quantity

            save_cart(
                user_id,
                items
            )

            return {
                "message": "Cart item quantity updated",
                "cart": items
            }

    # Add new product
    new_item = CartItem(
        product_id=request.product_id,
        product_name=request.product_name,
        price=request.price,
        quantity=request.quantity
    )

    items.append(new_item)

    save_cart(
        user_id,
        items
    )

    return {
        "message": "Product added to cart",
        "cart": items
    }


# Update cart item quantity
@app.put("/cart/{user_id}/items/{product_id}")
def update_cart_item(
    user_id: int,
    product_id: int,
    request: UpdateCartRequest
):
    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    items = load_cart(user_id)

    for item in items:

        if item.product_id == product_id:

            item.quantity = request.quantity

            save_cart(
                user_id,
                items
            )

            return {
                "message": "Cart item updated",
                "cart": items
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in cart"
    )


# Remove item from cart
@app.delete("/cart/{user_id}/items/{product_id}")
def remove_from_cart(
    user_id: int,
    product_id: int
):
    items = load_cart(user_id)

    for item in items:

        if item.product_id == product_id:

            items.remove(item)

            save_cart(
                user_id,
                items
            )

            return {
                "message": "Product removed from cart",
                "cart": items
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found in cart"
    )


# Clear entire cart
@app.delete("/cart/{user_id}")
def clear_cart(user_id: int):

    redis_client.delete(
        get_cart_key(user_id)
    )

    return {
        "message": "Cart cleared successfully"
    }
