# app/main.py
from fastapi import FastAPI
from .database import Base, engine
from .routers import cars, customers, salesmen, transactions

# Create database tables automatically if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dealership AI-Native CRM API")

# Mount Routers
app.include_router(cars.router)
app.include_router(customers.router)
app.include_router(salesmen.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "Dealership CRM API is live!"}
