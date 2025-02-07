from fastapi import APIRouter, Depends, HTTPException, status, Request
import json
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from schemas.user import UserCreate, UserGetAll
from crud.user import create_user, get_user_by_username
from api.deps import get_db
from models.users import User as DBUser
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    print(json.dumps(body, indent=4))  # Debugging: Print the incoming request data

    # Convert string UUIDs to UUID
    if 'defPrescriber' in body and body['defPrescriber']:
        body['defPrescriber'] = UUID(body['defPrescriber'])
    if 'defCustomerOID' in body and body['defCustomerOID']:
        body['defCustomerOID'] = UUID(body['defCustomerOID'])
    if 'employeeID' in body and body['employeeID']:
        body['employeeID'] = UUID(body['employeeID'])

    # Check for existing user with the same userName_str
    existing_user = db.query(DBUser).filter(DBUser.userName_str == body['userName_str']).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    user = UserCreate(**body)
    db_user = DBUser(**user.dict(exclude={'userID'}))  # Exclude userID from the insert statement

    try:
        # Set IDENTITY_INSERT to ON
        db.execute(text("SET IDENTITY_INSERT tbSystem_Users ON"))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    finally:
        # Set IDENTITY_INSERT to OFF
        db.execute(text("SET IDENTITY_INSERT tbSystem_Users OFF"))

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully", "user": str(db_user.userID)})

@router.get("/{user_id}", response_model=UserGetAll)
async def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.userID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserGetAll.from_orm(db_user)

@router.get("/", response_model=List[UserGetAll])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(DBUser).all()
    return [UserGetAll.from_orm(user) for user in users]