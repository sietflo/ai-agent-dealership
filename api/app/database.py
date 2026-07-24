# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database connection URL format:
# postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
DATABASE_URL = "postgresql+psycopg://crm_admin:crm_admin@localhost:5432/dealership_db"

# Create the engine that manages connections to PostgreSQL
engine = create_engine(DATABASE_URL, echo=True)  # echo=True prints raw SQL queries in logs for debugging

# Session maker to generate database sessions for CRUD operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our table models will inherit from
Base = declarative_base()

def get_db():
    """Helper to acquire a database session and close it automatically when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()