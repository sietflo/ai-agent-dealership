# app/schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# ==========================================
# 1. SALESMAN SCHEMAS
# ==========================================
class SalesmanBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SalesmanCreate(SalesmanBase):
    pass

class SalesmanUpdate(BaseModel):
    """PATCH /salesmen/{id}"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class SalesmanResponse(SalesmanBase):
    id: int

    # ConfigDict(from_attributes=True) tells Pydantic to automatically read
    # SQLAlchemy database objects and convert them into JSON responses.
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 2. CUSTOMER SCHEMAS
# ==========================================
class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    """PATCH /customers/{id}"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerResponse(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 3. CAR SCHEMAS
# ==========================================
class CarBase(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
    make: str
    model: str
    price: float = Field(..., gt=0, description="Price must be greater than 0")


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    """Used for PATCH requests when updating specific fields."""
    make: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None  # e.g., 'AVAILABLE', 'SOLD', 'RESERVED'


class CarResponse(CarBase):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# 4. TRANSACTION SCHEMAS
# ==========================================
class TransactionCreate(BaseModel):
    car_id: int
    customer_id: int
    salesman_id: int
    sale_price: float = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: int
    sale_price: float
    created_at: datetime
    car: CarResponse
    customer: CustomerResponse
    salesman: SalesmanResponse

    model_config = ConfigDict(from_attributes=True)