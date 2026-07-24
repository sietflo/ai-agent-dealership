#app/routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, auth
from ..database import get_db
from ..models import Transaction, Car, Customer, Salesman
from ..schemas import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# 1. LIST ALL TRANSACTIONS
@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch all completed sales transactions with joined car, customer, and salesman data."""
    return db.query(Transaction).all()

# 2. GET A SINGLE TRANSACTION BY ID
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch details of a specific transaction by its ID."""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
        txn_data: TransactionCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """
    Log a new vehicle sale transaction.
    Checks foreign key existence and marks the car status as 'SOLD'.
    """
    # Verify the Car exists
    car = db.query(Car).filter(Car.id == txn_data.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Prevent selling a car that has already been sold
    if car.status == "SOLD":
        raise HTTPException(status_code=400, detail="Car is already marked as SOLD")

    # Verify Customer exists
    customer = db.query(Customer).filter(Customer.id == txn_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Verify Salesman exists
    salesman = db.query(Salesman).filter(Salesman.id == txn_data.salesman_id).first()
    if not salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")

    new_txn = Transaction(**txn_data.model_dump())
    db.add(new_txn)

    # 2. Update the Car status to SOLD in the same DB transaction session
    car.status = "SOLD"
    db.commit()
    db.refresh(new_txn)

    return new_txn