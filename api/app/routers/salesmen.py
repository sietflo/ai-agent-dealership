#app/routers/salesmen.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, auth
from ..database import  get_db
from ..models import Salesman
from ..schemas import SalesmanCreate, SalesmanResponse, SalesmanUpdate

router = APIRouter(prefix="/salesmen", tags=["salesmen"])

# 1. LIST ALL Salesmen
@router.get("/", response_model=List[SalesmanResponse])
def list_salesmen(
        query: Optional[str] = Query(None, description="Search salesman by name or email"),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch all Salesmen or filter by multi-word name or email if query is provided."""
    db_query = db.query(Salesman)

    if query and query.strip():
        search_terms = query.strip().split()
        for term in search_terms:
            t = f"%{term}%"
            # Every word in the query must match first_name, last_name, or email
            db_query = db_query.filter(
                (Salesman.first_name.ilike(t)) |
                (Salesman.last_name.ilike(t)) |
                (Salesman.email.ilike(t))
            )

    return db_query.all()

# 2. GET A SINGLE Salesman BY ID
@router.get("/{salesman_id}", response_model=SalesmanResponse)
def get_salesman(
        salesman_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Fetch a single Salesman by their primary key ID."""
    salesman = db.query(Salesman).filter(Salesman.id == salesman_id).first()
    if not salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")
    return salesman

# 3. CREATE A NEW Salesman
@router.post("/", response_model=SalesmanResponse, status_code=status.HTTP_201_CREATED)
def create_salesman(
        Salesman_data: SalesmanCreate,
        db: Session=Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Create a new Salesman (ensures email is unique)."""
    existing_Salesman = db.query(Salesman).filter(Salesman.email == Salesman_data.email).first()
    if existing_Salesman:
        raise HTTPException(status_code=400, detail="Salesman already exists")
    new_Salesman = Salesman(**Salesman_data.model_dump())
    db.add(new_Salesman)
    db.commit()
    db.refresh(new_Salesman)
    return new_Salesman

# 4. UPDATE A Salesman (PATCH)
@router.patch("/{salesman_id}", response_model=SalesmanResponse)
def update_salesman(
        salesman_id: int,
        salesman_data: SalesmanUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_user)):
    """Update specific fields of an existing Salesman."""
    db_salesman = db.query(Salesman).filter(Salesman.id == salesman_id).first()
    if not db_salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")
    update_dict = salesman_data.model_dump(exclude_unset=True)

    if "email" in update_dict and update_dict["email"] != db_salesman.email:
        existing_email = db.query(Salesman).filter(Salesman.email == update_dict["email"]).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="This email is already used")
    for key, value in update_dict.items():
        setattr(db_salesman, key, value)
    db.commit()
    db.refresh(db_salesman)
    return db_salesman


