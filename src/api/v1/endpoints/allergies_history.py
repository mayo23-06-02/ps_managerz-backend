# src/api/v1/endpoints/allergies_history.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from src.schemas.allergies_history import AllergyHistoryCreate, AllergyHistoryResponse
from src.database.session import get_db
from src.models.allergies_history import ClientAllergyEditHistory

router = APIRouter()

@router.post("/", response_model=AllergyHistoryResponse)
async def create_allergy_history(
    history_data: AllergyHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new allergy edit history record.
    
    - Automatically generates OID
    - Sets lastUpdateDate_dat to current time if not provided
    - Returns the created history record
    """
    # Create history record with generated OID
    history_dict = history_data.dict()
    history_dict["OID"] = uuid4()
    history_dict["lastUpdateDate_dat"] = datetime.utcnow()
    
    db_history = ClientAllergyEditHistory(**history_dict)
    
    try:
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return db_history

@router.get("/{history_id}", response_model=AllergyHistoryResponse)
async def get_history_record(
    history_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific history record by its OID.
    
    - Returns the complete history record
    - Raises 404 if record not found
    """
    db_history = db.query(ClientAllergyEditHistory).filter(ClientAllergyEditHistory.OID == history_id).first()
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {history_id} not found"
        )
    
    return db_history

@router.get("/allergy/{allergy_id}", response_model=List[AllergyHistoryResponse])
async def get_allergy_history(
    allergy_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all history records for a specific allergy.
    
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no records found
    - Sorts by lastUpdateDate_dat in descending order (newest first)
    """
    history_records = db.query(ClientAllergyEditHistory)\
        .filter(ClientAllergyEditHistory.itemsOID == allergy_id)\
        .order_by(ClientAllergyEditHistory.lastUpdateDate_dat.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return history_records

@router.get("/user/{user_id}", response_model=List[AllergyHistoryResponse])
async def get_user_history(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all history records created by a specific user.
    
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no records found
    - Sorts by lastUpdateDate_dat in descending order (newest first)
    """
    history_records = db.query(ClientAllergyEditHistory)\
        .filter(ClientAllergyEditHistory.userID == user_id)\
        .order_by(ClientAllergyEditHistory.lastUpdateDate_dat.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return history_records

@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_record(
    history_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a history record.
    
    - Requires history_id in the path
    - Returns 204 No Content on success
    - Raises 404 if record not found
    """
    db_history = db.query(ClientAllergyEditHistory).filter(ClientAllergyEditHistory.OID == history_id).first()
    if not db_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {history_id} not found"
        )
    
    try:
        db.delete(db_history)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return None
