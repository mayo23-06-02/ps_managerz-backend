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

# Test function to check if the connection is successful
def test_connection():
    try:
        # Attempt to create a session
        session = SessionLocal()
        # Execute a simple query
        session.execute(text('SELECT 1'))
        # Close the session
        session.close()
        print("Connection successful!")
    except OperationalError:
        print("Connection failed!")

# Call the test function
test_connection()

