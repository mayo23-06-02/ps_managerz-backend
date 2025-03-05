# src/database/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

# Use MSSQL connection string from settings
SQLALCHEMY_DATABASE_URL = 'mssql+pyodbc://FastAPI:Sumsangs7@192.168.1.3,1433/Ps_RFM?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()