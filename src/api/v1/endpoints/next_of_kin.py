# src/api/v1/endpoints/next_of_kin.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID, uuid4
from typing import List, Optional
from fastapi.responses import JSONResponse
from datetime import datetime

from src.schemas.next_of_kin import (
    NextOfKinCreate, 
    NextOfKinUpdate, 
    NextOfKinDelete,
    NextOfKinResponse,
    NextOfKinResponseMessage
)
from src.database.session import get_db
from src.models.next_of_kin import ClientNextOfKin

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NextOfKinResponseMessage)
async def create_next_of_kin(
    next_of_kin: NextOfKinCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new next of kin record for a client.
    
    - Requires firstName_str, relationship_str, and clientOID
    - Automatically generates OID
    - Returns the created record's OID and a success message
    """
    # Check if client exists (assuming you have a Client model)
    # client = db.query(Client).filter(Client.OID == next_of_kin.clientOID).first()
    # if not client:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Client with ID {next_of_kin.clientOID} not found"
    #     )
    
    # Create next of kin instance
    db_next_of_kin = ClientNextOfKin(
        OID=uuid4(),
        **next_of_kin.dict(),
        addedDate_dat=datetime.utcnow(),
        deleted_bol=False
    )
    
    try:
        db.add(db_next_of_kin)
        db.commit()
        db.refresh(db_next_of_kin)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Next of kin record created successfully",
        "next_of_kin_id": str(db_next_of_kin.OID)
    }

@router.get("/{record_id}", response_model=NextOfKinResponse)
async def get_next_of_kin(
    record_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve a next of kin record by its OID.
    
    - Returns the complete record information
    - Raises 404 if record not found
    """
    db_record = db.query(ClientNextOfKin).filter(ClientNextOfKin.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Next of kin record with ID {record_id} not found"
        )
    
    return db_record

@router.get("/client/{client_id}", response_model=List[NextOfKinResponse])
async def get_client_next_of_kin(
    client_id: UUID,
    active_only: bool = Query(False, description="Filter out deleted records"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all next of kin records for a specific client.
    
    - Supports filtering active/deleted records
    - Returns an empty list if no records found
    """
    query = db.query(ClientNextOfKin).filter(ClientNextOfKin.clientOID == client_id)
    
    if active_only:
        query = query.filter(ClientNextOfKin.deleted_bol == False)
    
    records = query.all()
    
    return records

@router.put("/{record_id}", response_model=NextOfKinResponseMessage)
async def update_next_of_kin(
    record_id: UUID,
    next_of_kin: NextOfKinUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing next of kin record.
    
    - Requires record_id in the path
    - Updates only the fields provided in the request
    - Cannot update a deleted record
    - Returns the updated record's OID and a success message
    """
    db_record = db.query(ClientNextOfKin).filter(ClientNextOfKin.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Next of kin record with ID {record_id} not found"
        )
    
    if db_record.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a deleted record"
        )
    
    # Update record attributes
    update_data = next_of_kin.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    # Update lastUpdateDate_dat
    db_record.lastUpdateDate_dat = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_record)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Next of kin record updated successfully",
        "next_of_kin_id": str(record_id)
    }

@router.delete("/{record_id}", response_model=NextOfKinResponseMessage)
async def delete_next_of_kin(
    record_id: UUID,
    delete_data: NextOfKinDelete,
    db: Session = Depends(get_db)
):
    """
    Soft delete a next of kin record.
    
    - Requires record_id in the path
    - Sets deleted_bol to True
    - Records who deleted it and why
    - Returns the deleted record's OID and a success message
    """
    db_record = db.query(ClientNextOfKin).filter(ClientNextOfKin.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Next of kin record with ID {record_id} not found"
        )
    
    if db_record.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Record is already deleted"
        )
    
    # Update delete fields
    db_record.deleted_bol = True
    db_record.deletedBy_str = delete_data.deletedBy_str
    db_record.deletetedReason_str = delete_data.deletetedReason_str
    db_record.lastUpdateDate_dat = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Next of kin record deleted successfully",
        "next_of_kin_id": str(record_id)
    }

@router.put("/restore/{record_id}", response_model=NextOfKinResponseMessage)
async def restore_next_of_kin(
    record_id: UUID,
    db: Session = Depends(get_db),
    updated_by: Optional[str] = Query(None, description="User who is restoring the record")
):
    """
    Restore a soft-deleted next of kin record.
    
    - Requires record_id in the path
    - Sets deleted_bol back to False
    - Clears deletion fields
    - Returns the restored record's OID and a success message
    """
    db_record = db.query(ClientNextOfKin).filter(ClientNextOfKin.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Next of kin record with ID {record_id} not found"
        )
    
    if not db_record.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Record is not deleted"
        )
    
    # Restore record
    db_record.deleted_bol = False
    db_record.deletedBy_str = None
    db_record.deletetedReason_str = None
    db_record.lastUpdateDate_dat = datetime.utcnow()
    db_record.lastUpdateBy_str = updated_by
    
    try:
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Next of kin record restored successfully",
        "next_of_kin_id": str(record_id)
    }

@router.post("/{record_id}/photo", response_model=NextOfKinResponseMessage)
async def upload_photo(
    record_id: UUID,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a photo for a next of kin record.
    
    - Requires record_id in the path
    - Accepts an image file
    - Updates the photo_img field
    - Returns the record's OID and a success message
    """
    db_record = db.query(ClientNextOfKin).filter(ClientNextOfKin.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Next of kin record with ID {record_id} not found"
        )
    
    if db_record.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a deleted record"
        )
    
    # Read and validate the photo
    content_type = photo.content_type
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    photo_data = await photo.read()
    if len(photo_data) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image size must be less than 5MB"
        )
    
    # Update the photo
    db_record.photo_img = photo_data
    db_record.lastUpdateDate_dat = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Photo uploaded successfully",
        "next_of_kin_id": str(record_id)
    }

@router.get("/search", response_model=List[NextOfKinResponse])
async def search_next_of_kin(
    name: Optional[str] = Query(None, description="Search by first or last name"),
    relationship: Optional[str] = Query(None, description="Filter by relationship type"),
    active_only: bool = Query(True, description="Filter out deleted records"),
    db: Session = Depends(get_db)
):
    """
    Search for next of kin records.
    
    - Supports searching by name
    - Supports filtering by relationship type
    - Supports filtering active/deleted records
    - Returns an empty list if no records found
    """
    query = db.query(ClientNextOfKin)
    
    if active_only:
        query = query.filter(ClientNextOfKin.deleted_bol == False)
    
    if name:
        query = query.filter(
            (ClientNextOfKin.firstName_str.ilike(f"%{name}%")) | 
            (ClientNextOfKin.lastName_str.ilike(f"%{name}%"))
        )
    
    if relationship:
        query = query.filter(ClientNextOfKin.relationship_str.ilike(f"%{relationship}%"))
    
    records = query.all()
    
    return records
