# src/api/v1/endpoints/allergies.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID, uuid4
from typing import List, Optional
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy import and_, or_, desc

from src.schemas.allergies import (
    AllergyCreate, 
    AllergyUpdate, 
    AllergyResponse,
    AllergyLock,
    AllergyActivation,
    AllergyPost,
    AllergyResponseMessage
)
from src.database.session import get_db
from src.models.allergies import ClientAllergy
from src.models.allergies_history import ClientAllergyEditHistory

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AllergyResponseMessage)
async def create_allergy(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Create a new client allergy record.
    
    - Requires allergyOID and clientOID
    - Automatically generates OID if not provided
    - Returns the created record's OID and a success message
    """
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid JSON body"
        )

    # Convert string UUIDs to UUID objects if present
    try:
        for uuid_field in ["OID", "allergyOID", "clientOID", "postedBy_GUID", "Rx_OID"]:
            if uuid_field in body and body[uuid_field]:
                body[uuid_field] = UUID(body[uuid_field])
        
        # Generate OID if not provided
        if "OID" not in body or not body["OID"]:
            body["OID"] = uuid4()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid UUID format: {str(e)}"
        )

    # Set default values for required fields if not provided
    if "nonActive_bol" not in body:
        body["nonActive_bol"] = False
    
    if "locked_bol" not in body:
        body["locked_bol"] = False

    # Validate against AllergyCreate schema
    try:
        allergy_data = AllergyCreate(**body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Validation error: {str(e)}"
        )

    # Check for existing record with same allergyOID and clientOID
    existing_record = db.query(ClientAllergy).filter(
        and_(
            ClientAllergy.allergyOID == allergy_data.allergyOID,
            ClientAllergy.clientOID == allergy_data.clientOID
        )
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Allergy record already exists for this client and allergy"
        )

    # Create ClientAllergy instance
    db_allergy = ClientAllergy(**body)

    # Create history record for creation
    history_record = ClientAllergyEditHistory(
        OID=uuid4(),
        editDescription1_str=f"Created new allergy record",
        editDescription2_str=f"Initial values: {', '.join([f'{k}={v}' for k, v in body.items() if v is not None])}",
        itemsOID=db_allergy.OID,
        username_str=body.get("postedBy_str"),
        userID=body.get("postedBy_GUID"),
        lastUpdateDate_dat=datetime.utcnow(),
        machine_str=body.get("machine_str"),
        machineID=body.get("machineID")
    )

    # Insert records
    try:
        db.add(db_allergy)
        db.add(history_record)
        db.commit()
        db.refresh(db_allergy)
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
        "message": "Allergy record created successfully", 
        "allergy_id": str(db_allergy.OID)
    }

@router.get("/{record_id}", response_model=AllergyResponse)
async def get_allergy(
    record_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Retrieve an allergy record by its OID.
    
    - Returns the complete record information
    - Raises 404 if record not found
    """
    db_record = db.query(ClientAllergy).filter(ClientAllergy.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allergy record with ID {record_id} not found"
        )
    return db_record

@router.get("/client/{client_id}", response_model=List[AllergyResponse])
async def get_client_allergies(
    client_id: UUID,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all allergy records for a specific client.
    
    - Supports filtering active/inactive allergies
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no records found
    """
    query = db.query(ClientAllergy).filter(ClientAllergy.clientOID == client_id)
    
    # Filter out inactive allergies if requested
    if not include_inactive:
        query = query.filter(or_(ClientAllergy.nonActive_bol.is_(None), ClientAllergy.nonActive_bol == False))
    
    # Apply pagination
    records = query.offset(skip).limit(limit).all()
    
    return records

@router.put("/{record_id}", response_model=AllergyResponseMessage)
async def update_allergy(
    record_id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update an existing allergy record.
    
    - Requires record_id in the path
    - Expects a JSON body with fields to update
    - Cannot update locked records unless explicitly unlocking
    - Creates a history record of the changes
    - Returns the updated record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAllergy).filter(ClientAllergy.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allergy record with ID {record_id} not found"
        )
    
    # Check if record is locked
    if db_record.locked_bol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot update a locked record"
        )
    
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid JSON body"
        )
    
    # Convert string UUIDs to UUID objects if present
    try:
        for uuid_field in ["postedBy_GUID", "Rx_OID"]:
            if uuid_field in body and body[uuid_field]:
                body[uuid_field] = UUID(body[uuid_field])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid UUID format: {str(e)}"
        )
    
    # Prevent changing OID, allergyOID, and clientOID
    for field in ["OID", "allergyOID", "clientOID"]:
        if field in body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot update {field}"
            )
    
    # Validate against AllergyUpdate schema
    try:
        update_data = AllergyUpdate(**body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Validation error: {str(e)}"
        )
    
    # Update nonActiveDate_dat if nonActive_bol is being set to True
    if "nonActive_bol" in body and body["nonActive_bol"] and not db_record.nonActive_bol:
        body["nonActiveDate_dat"] = datetime.utcnow()
    
    # Create history record before updating
    history_record = ClientAllergyEditHistory(
        OID=uuid4(),
        editDescription1_str=f"Updated allergy record: {', '.join([f'{k}={v}' for k, v in body.items()])}",
        editDescription2_str=f"Previous values: {', '.join([f'{k}={getattr(db_record, k)}' for k in body.keys() if hasattr(db_record, k)])}",
        itemsOID=record_id,
        username_str=body.get("postedBy_str"),
        userID=body.get("postedBy_GUID"),
        lastUpdateDate_dat=datetime.utcnow(),
        machine_str=getattr(db_record, "machine_str", None),
        machineID=getattr(db_record, "machineID", None)
    )
    
    # Update record attributes
    try:
        # Add history record
        db.add(history_record)
        
        # Update allergy record
        for key, value in body.items():
            setattr(db_record, key, value)
        
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
        "message": "Allergy record updated successfully", 
        "allergy_id": str(record_id)
    }

@router.delete("/{record_id}", response_model=AllergyResponseMessage)
async def delete_allergy(
    record_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an allergy record.
    
    - Requires record_id in the path
    - Cannot delete locked or posted records
    - Permanently removes the record from the database
    - Creates a history record of the deletion
    - Returns the deleted record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAllergy).filter(ClientAllergy.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allergy record with ID {record_id} not found"
        )
    
    # Check if record is locked
    if db_record.locked_bol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete a locked record"
        )
    
    # Check if record is posted
    if getattr(db_record, "posted_bol", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete a posted record"
        )
    
    # Create history record for deletion
    history_record = ClientAllergyEditHistory(
        OID=uuid4(),
        editDescription1_str=f"Deleted allergy record",
        editDescription2_str=f"Deleted values: {', '.join([f'{k}={getattr(db_record, k)}' for k in ['allergyOID', 'clientOID', 'allergyName_str'] if hasattr(db_record, k)])}",
        itemsOID=record_id,
        lastUpdateDate_dat=datetime.utcnow()
    )
    
    try:
        # Add history record
        db.add(history_record)
        
        # Delete allergy record
        db.delete(db_record)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Allergy record deleted successfully", 
        "allergy_id": str(record_id)
    }


@router.patch("/{record_id}/lock", response_model=AllergyResponseMessage)
async def lock_allergy(
    record_id: UUID,
    lock_data: AllergyLock,
    db: Session = Depends(get_db)
):
    """
    Lock or unlock an allergy record.
    
    - Requires record_id in the path
    - Expects a JSON body with locked_bol and optionally lockedBy_str
    - Updates lockedDate_dat automatically
    - Returns the record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAllergy).filter(ClientAllergy.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allergy record with ID {record_id} not found"
        )
    
    try:
        # Update lock status
        db_record.locked_bol = lock_data.locked_bol
        
        if lock_data.locked_bol:
            db_record.lockedBy_str = lock_data.lockedBy_str
            db_record.lockedDate_dat = datetime.utcnow()
        else:
            db_record.lockedBy_str = None
            db_record.lockedDate_dat = None
        
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )
    
    action = "locked" if lock_data.locked_bol else "unlocked"
    return {
        "message": f"Allergy record {action} successfully", 
        "allergy_id": str(record_id)
    }

@router.patch("/{record_id}/activate", response_model=AllergyResponseMessage)
async def set_allergy_active_status(
    record_id: UUID,
    activation: AllergyActivation,
    db: Session = Depends(get_db)
):
    """
    Set the active/inactive status of an allergy record.
    
    - Requires record_id in the path
    - Expects a JSON body with nonActive_bol and optionally nonActiveDate_dat
    - Updates nonActiveDate_dat automatically if not provided
    - Returns the record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAllergy).filter(ClientAllergy.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Allergy record with ID {record_id} not found"
        )
    
    # Check if record is locked
    if db_record.locked_bol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot update a locked record"
        )
    
    try:
        # Update active status
        db_record.nonActive_bol = activation.nonActive_bol
        
        # If setting to inactive and no date provided, use current time
        if activation.nonActive_bol:
            db_record.nonActiveDate_dat = activation.nonActiveDate_dat or datetime.utcnow()
        else:
            db_record.nonActiveDate_dat = None
        
        db.commit()
        db.refresh(db_record)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )
    
    status_text = "inactive" if activation.nonActive_bol else "active"
    return {
        "message": f"Allergy record set to {status_text} successfully", 
        "allergy_id": str(record_id)
    }

