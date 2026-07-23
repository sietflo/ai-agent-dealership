# app/main.py
from fastapi import FastAPI
from .database import Base, engine
from .routers import cars, customers, salesmen, transactions, auth
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
# Create database tables automatically if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dealership AI-Native CRM API")

# Mount Routers
app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(customers.router)
app.include_router(salesmen.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "Dealership CRM API is live!"}

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": f"HTTP_{exc.status_code}", "message": exc.detail},
    )