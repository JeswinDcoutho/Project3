from fastapi import FastAPI, Depends, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
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
POSTGRES_DB = os.getenv("POSTGRES_DB", "payment_db")

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


class PaymentDB(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Payment Service",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)



class PaymentRequest(BaseModel):
    order_id: int
    user_id: int
    amount: float
    payment_method: str


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "payment-service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/payments")
def create_payment(
    request: PaymentRequest,
    db: Session = Depends(get_db)
):

    if request.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Payment amount must be greater than 0"
        )

    payment = PaymentDB(
        order_id=request.order_id,
        user_id=request.user_id,
        amount=request.amount,
        payment_method=request.payment_method,
        status="Completed"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment processed successfully",
        "payment": payment
    }


@app.get("/payments")
def get_payments(
    db: Session = Depends(get_db)
):

    return db.query(PaymentDB).all()


@app.get("/payments/{payment_id}")
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):

    payment = db.query(PaymentDB).filter(
        PaymentDB.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment


@app.get("/payments/order/{order_id}")
def get_order_payment(
    order_id: int,
    db: Session = Depends(get_db)
):

    payment = db.query(PaymentDB).filter(
        PaymentDB.order_id == order_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found for this order"
        )

    return payment


@app.put("/payments/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    payment = db.query(PaymentDB).filter(
        PaymentDB.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    allowed_statuses = [
        "Pending",
        "Completed",
        "Failed",
        "Refunded"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed values: {allowed_statuses}"
        )

    payment.status = status

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment status updated",
        "payment": payment
    }
