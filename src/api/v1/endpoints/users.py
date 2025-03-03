# src/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List, Optional
from fastapi.responses import JSONResponse
from sqlalchemy import text
from datetime import datetime

from src.schemas.user import UserCreate, UserGetAll
from src.database.session import get_db
from src.models.user import User as DBUser
from src.core.security import pwd_context

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_user_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Create a new system user in tbSystem_Users.
    Expects a JSON body matching the UserCreate schema.
    Generates userID if not provided, using IDENTITY_INSERT.
    Returns a success message with the created user's ID.
    """
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    # Convert string UUIDs to UUID objects if present
    try:
        if "defPrescriber" in body and body["defPrescriber"]:
            body["defPrescriber"] = UUID(body["defPrescriber"])
        if "defCustomerOID" in body and body["defCustomerOID"]:
            body["defCustomerOID"] = UUID(body["defCustomerOID"])
        if "employeeID" in body and body["employeeID"]:
            body["employeeID"] = UUID(body["employeeID"])
        if "userID" in body and body["userID"]:
            body["userID"] = UUID(body["userID"])
        else:
            body["userID"] = uuid4()  # Generate userID if not provided
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid UUID format: {str(e)}")

    # Validate against UserCreate schema
    try:
        user = UserCreate(**body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}")

    # Check for existing user by username
    existing_user = db.query(DBUser).filter(DBUser.userName_str == user.userName_str).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")

    # Hash the password
    hashed_password = pwd_context.hash(user.password_str)

    # Create DBUser instance with userID
    db_user_data = user.dict(exclude={"password_str"})
    db_user_data["password_str"] = hashed_password
    db_user = DBUser(**db_user_data)

    # Insert with IDENTITY_INSERT ON
    try:
        db.execute(text("SET IDENTITY_INSERT tbSystem_Users ON"))
        db.add(db_user)
        db.commit()
        db.execute(text("SET IDENTITY_INSERT tbSystem_Users OFF"))
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    finally:
        db.execute(text("SET IDENTITY_INSERT tbSystem_Users OFF"))
        db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully", "user": str(db_user.userID)}
    )

@router.get("/{user_id}", response_model=UserGetAll)
async def read_user(user_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a user by their UUID.
    """
    try:
        db_user = db.query(DBUser).filter(DBUser.userID == user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserGetAll.from_orm(db_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving user: {str(e)}")

@router.get("/", response_model=List[UserGetAll])
async def read_users(db: Session = Depends(get_db)):
    """
    Retrieve all users.
    """
    try:
        users = db.query(DBUser).all()
        if not users:
            return []
        return [UserGetAll.from_orm(user) for user in users]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving users: {str(e)}")

@router.put("/{user_id}", response_model=UserGetAll)
async def update_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update an existing user by their UUID.
    Expects a JSON body matching the UserCreate schema (partial updates allowed).
    """
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    # Convert string UUIDs to UUID objects if present
    try:
        if "defPrescriber" in body and body["defPrescriber"]:
            body["defPrescriber"] = UUID(body["defPrescriber"])
        if "defCustomerOID" in body and body["defCustomerOID"]:
            body["defCustomerOID"] = UUID(body["defCustomerOID"])
        if "employeeID" in body and body["employeeID"]:
            body["employeeID"] = UUID(body["employeeID"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid UUID format: {str(e)}")

    # Validate against UserCreate schema
    try:
        user_update = UserCreate(**body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}")

    db_user = db.query(DBUser).filter(DBUser.userID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check for username conflict with another user
    if user_update.userName_str != db_user.userName_str:
        existing_user = db.query(DBUser).filter(DBUser.userName_str == user_update.userName_str).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken by another user")

    # Update fields from the request
    update_data = user_update.dict(exclude_unset=True)
    if "password_str" in update_data:
        update_data["password_str"] = pwd_context.hash(update_data["password_str"])
    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return UserGetAll.from_orm(db_user)

@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_user(
    user_id: UUID,
    deleted_by: str = "system",
    reason: str = "Requested by user",
    db: Session = Depends(get_db)
):
    """
    Soft delete a user by their UUID.
    Sets deleted_bol to True with deletion details.
    """
    db_user = db.query(DBUser).filter(DBUser.userID == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if db_user.deleted_bol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already deleted")

    try:
        db_user.deleted_bol = True
        db_user.deletedBy_str = deleted_by
        db_user.deletedDate_dat = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User deleted successfully", "user": str(db_user.userID)}
    )