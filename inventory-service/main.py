import os
from prometheus_fastapi_instrumentator import Instrumentator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker


load_dotenv()


# ============================================================
# Database Configuration
# ============================================================

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "inventory_db")


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


# ============================================================
# Database Model
# ============================================================

class InventoryDB(Base):
    __tablename__ = "inventory"

    product_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_name = Column(
        String,
        nullable=False
    )

    stock = Column(
        Integer,
        nullable=False
    )

    reserved = Column(
        Integer,
        nullable=False,
        default=0
    )

    status = Column(
        String,
        nullable=False,
        default="Available"
    )


Base.metadata.create_all(bind=engine)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="E-Commerce Inventory Service",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(app)


# ============================================================
# Request Models
# ============================================================

class InventoryRequest(BaseModel):
    product_id: int
    product_name: str
    stock: int


class StockUpdateRequest(BaseModel):
    quantity: int


# ============================================================
# Database Dependency
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# Helper Functions
# ============================================================

def calculate_status(stock: int, reserved: int) -> str:
    available_stock = stock - reserved

    if available_stock <= 0:
        return "OutOfStock"

    return "Available"


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "service": "inventory-service",
        "status": "running"
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


# ============================================================
# Get All Inventory
# ============================================================

@app.get("/inventory")
def get_inventory(
    db: Session = Depends(get_db)
):
    return db.query(InventoryDB).all()


# ============================================================
# Get Inventory by Product ID
# ============================================================

@app.get("/inventory/{product_id}")
def get_inventory_item(
    product_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(InventoryDB).filter(
        InventoryDB.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product inventory not found"
        )

    return item


# ============================================================
# Add New Inventory
# ============================================================

@app.post("/inventory")
def add_inventory(
    request: InventoryRequest,
    db: Session = Depends(get_db)
):
    if request.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    existing_item = db.query(InventoryDB).filter(
        InventoryDB.product_id == request.product_id
    ).first()

    if existing_item:
        raise HTTPException(
            status_code=409,
            detail="Product inventory already exists"
        )

    status = (
        "Available"
        if request.stock > 0
        else "OutOfStock"
    )

    item = InventoryDB(
        product_id=request.product_id,
        product_name=request.product_name,
        stock=request.stock,
        reserved=0,
        status=status
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Inventory added successfully",
        "inventory": item
    }


# ============================================================
# Update Stock
# ============================================================

@app.put("/inventory/{product_id}/stock")
def update_stock(
    product_id: int,
    request: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    item = db.query(InventoryDB).filter(
        InventoryDB.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product inventory not found"
        )

    new_stock = item.stock + request.quantity

    if new_stock < item.reserved:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be lower than reserved quantity"
        )

    item.stock = new_stock

    if item.status != "Discontinued":
        item.status = calculate_status(
            item.stock,
            item.reserved
        )

    db.commit()
    db.refresh(item)

    return {
        "message": "Stock updated successfully",
        "inventory": item
    }


# ============================================================
# Reserve Stock
# ============================================================

@app.post("/inventory/{product_id}/reserve")
def reserve_stock(
    product_id: int,
    request: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    item = db.query(InventoryDB).filter(
        InventoryDB.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product inventory not found"
        )

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Reservation quantity must be greater than 0"
        )

    available_stock = item.stock - item.reserved

    if request.quantity > available_stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient available stock"
        )

    item.reserved += request.quantity

    if item.status != "Discontinued":
        item.status = calculate_status(
            item.stock,
            item.reserved
        )

    db.commit()
    db.refresh(item)

    return {
        "message": "Stock reserved successfully",
        "inventory": item
    }


# ============================================================
# Release Reserved Stock
# ============================================================

@app.post("/inventory/{product_id}/release")
def release_stock(
    product_id: int,
    request: StockUpdateRequest,
    db: Session = Depends(get_db)
):
    item = db.query(InventoryDB).filter(
        InventoryDB.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product inventory not found"
        )

    if request.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Release quantity must be greater than 0"
        )

    if request.quantity > item.reserved:
        raise HTTPException(
            status_code=400,
            detail="Cannot release more stock than reserved"
        )

    item.reserved -= request.quantity

    if item.status != "Discontinued":
        item.status = calculate_status(
            item.stock,
            item.reserved
        )

    db.commit()
    db.refresh(item)

    return {
        "message": "Reserved stock released successfully",
        "inventory": item
    }


# ============================================================
# Update Inventory Status
# ============================================================

@app.put("/inventory/{product_id}/status")
def update_inventory_status(
    product_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    item = db.query(InventoryDB).filter(
        InventoryDB.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product inventory not found"
        )

    allowed_statuses = [
        "Available",
        "OutOfStock",
        "Discontinued"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    item.status = status

    db.commit()
    db.refresh(item)

    return {
        "message": "Inventory status updated",
        "inventory": item
    }
