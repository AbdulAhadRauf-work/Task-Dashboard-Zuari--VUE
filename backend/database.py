
# backend/database.py
# --- Final Version ---

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL.
# 'sqlite:///./task_dashboard.db' creates the file in the same directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./task_dashboard.db"

# Create the SQLAlchemy engine.
# The 'check_same_thread' argument is needed only for SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our ORM models will inherit from this class.
Base = declarative_base()
