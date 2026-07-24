#app/routers/customers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, auth
from ..database import  get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerResponse, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["Customers"])

# 1. LIST ALL CUSTOMERS
from typing import List, Optional

@router.get("/", response_model=List[CustomerResponse])
def list_customers(
        query: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch customers, optionally filtered by name or email."""
    q = db.query(Customer)
    if query:
        q = q.filter(
            (Customer.first_name.ilike(f"%{query}%")) |
            (Customer.last_name.ilike(f"%{query}%")) |
            (Customer.email.ilike(f"%{query}%"))
        )
    return q.all()

# 2. GET A SINGLE CUSTOMER BY ID
@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
        customer_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch a single customer by their primary key ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# 3. CREATE A NEW CUSTOMER
@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
        customer_data: CustomerCreate,
        db: Session=Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Create a new customer (ensures email is unique)."""
    existing_customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer already exists")
    new_customer = Customer(**customer_data.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

# 4. UPDATE A CUSTOMER (PATCH)
@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
        customer_id: int,
        customer_data: CustomerUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Update specific fields of an existing customer."""
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        raise  HTTPException(status_code=404, detail="Customer not found")
    update_dict = customer_data.model_dump(exclude_unset=True)

    if "email" in update_dict and update_dict["email"] != db_customer.email:
        existing_email = db.query(Customer).filter(Customer.email == update_dict["email"]).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="This email is already used")
    for key, value in update_dict.items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer


