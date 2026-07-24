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
    phone: Optional[str] = None

class SalesmanCreate(SalesmanBase):
    pass

class SalesmanUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

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
    phone: Optional[str] = None



class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

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
    year: int = Field(..., ge=1900, le=2100)
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    status: str = "AVAILABLE"


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




from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None