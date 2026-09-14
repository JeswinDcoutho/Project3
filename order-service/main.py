from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
import os


load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "order_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, nullable=False)


class OrderItemDB(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )
    product_id = Column(Integer, nullable=False)
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="E-Commerce Order Service",
    version="1.0.0"
)


class OrderItem(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int


class CreateOrderRequest(BaseModel):
    user_id: int
    items: List[OrderItem]


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "order-service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/orders")
def create_order(
    request: CreateOrderRequest,
    db: Session = Depends(get_db)
):

    if not request.items:
        raise HTTPException(
            status_code=400,
            detail="Order must contain at least one item"
        )

    for item in request.items:

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than 0"
            )

        if item.price < 0:
            raise HTTPException(
                status_code=400,
                detail="Price cannot be negative"
            )

    total = sum(
        item.price * item.quantity
        for item in request.items
    )

    order = OrderDB(
        user_id=request.user_id,
        total=total,
        status="Pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in request.items:

        order_item = OrderItemDB(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            price=item.price,
            quantity=item.quantity
        )

        db.add(order_item)

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "user_id": order.user_id,
        "total": order.total,
        "status": order.status,
        "items": request.items
    }


@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):

    orders = db.query(OrderDB).all()

    result = []

    for order in orders:

        items = db.query(OrderItemDB).filter(
            OrderItemDB.order_id == order.id
        ).all()

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "items": items,
            "total": order.total,
            "status": order.status
        })

    return result


@app.get("/orders/user/{user_id}")
def get_user_orders(
    user_id: int,
    db: Session = Depends(get_db)
):

    orders = db.query(OrderDB).filter(
        OrderDB.user_id == user_id
    ).all()

    result = []

    for order in orders:

        items = db.query(OrderItemDB).filter(
            OrderItemDB.order_id == order.id
        ).all()

        result.append({
            "id": order.id,
            "user_id": order.user_id,
            "items": items,
            "total": order.total,
            "status": order.status
        })

    return result


@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    order = db.query(OrderDB).filter(
        OrderDB.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    items = db.query(OrderItemDB).filter(
        OrderItemDB.order_id == order.id
    ).all()

    return {
        "id": order.id,
        "user_id": order.user_id,
        "items": items,
        "total": order.total,
        "status": order.status
    }


@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    order = db.query(OrderDB).filter(
        OrderDB.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Processing",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    order.status = status

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status
    }
