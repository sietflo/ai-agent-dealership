# app/routers/cars.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, auth
from ..database import get_db
from ..models import Car
from ..schemas import CarCreate, CarResponse, CarUpdate

router = APIRouter(prefix="/cars", tags=["Cars"])


# 1. GET ALL CARS (Protected, with optional status filter)
@router.get("/", response_model=List[CarResponse])
def list_cars(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(Car)
    if status:
        query = query.filter(Car.status.ilike(status))
    return query.all()


# 2. GET SINGLE CAR BY ID (Protected)
@router.get("/{car_id}", response_model=CarResponse)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


# 3. CREATE A CAR (Protected)
@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(
    car_data: CarCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if VIN already exists
    existing_car = db.query(Car).filter(Car.vin == car_data.vin).first()
    if existing_car:
        raise HTTPException(status_code=400, detail="Car with this VIN already exists")

    new_car = Car(**car_data.model_dump())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


# 4. UPDATE A CAR (Protected)
@router.patch("/{car_id}", response_model=CarResponse)
def update_car(
    car_id: int,
    car_data: CarUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_car = db.query(Car).filter(Car.id == car_id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Exclude fields that were not provided in the request
    update_dict = car_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_car, key, value)

    db.commit()
    db.refresh(db_car)
    return db_car