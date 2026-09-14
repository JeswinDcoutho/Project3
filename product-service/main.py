from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
import os


load_dotenv()


POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "product_db")

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


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="E-Commerce Product Service",
    version="1.0.0"
)


class ProductCreate(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "product-service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/products")
def get_products(db: Session = Depends(get_db)):

    return db.query(ProductDB).all()


@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(ProductDB).filter(
        ProductDB.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.post("/products")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = db.query(ProductDB).filter(
        ProductDB.id == product.id
    ).first()

    if existing_product:
        raise HTTPException(
            status_code=409,
            detail="Product already exists"
        )

    if product.price < 0:
        raise HTTPException(
            status_code=400,
            detail="Price cannot be negative"
        )

    if product.stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Stock cannot be negative"
        )

    new_product = ProductDB(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product": new_product
    }
