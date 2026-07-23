# models.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Salesman(Base):
    __tablename__ = "salesmen"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    transactions = relationship("Transaction", back_populates="salesman")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    transactions = relationship("Transaction", back_populates="customer")

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String, unique=True, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="AVAILABLE") # AVAILABLE, SOLD

    transaction = relationship("Transaction", back_populates="car", uselist=False)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    salesman_id = Column(Integer, ForeignKey("salesmen.id"), nullable=False)
    sale_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    car = relationship("Car", back_populates="transaction")
    customer = relationship("Customer", back_populates="transactions")
    salesman = relationship("Salesman", back_populates="transactions")