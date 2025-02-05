from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User, Post  # Directly import User and Post

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic schemas
class UserCreate(BaseModel):
    email: str
    username: str
class UserRead(BaseModel):
    id: int
    email: str
    username: str 

# Example endpoint
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully", "user": db_user.id})

# GET endpoint to fetch a user by ID
@app.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# GET endpoint to fetch all users
@app.get("/users/", response_model=List[UserRead])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users 