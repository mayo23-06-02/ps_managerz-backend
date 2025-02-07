from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = ( 
    
    "mssql+pyodbc://MAYO23\\SQL17/Ps_RFM?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # Used by models.py

