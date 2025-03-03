# src/api/v1/endpoints/anthropometrics.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID, uuid4
from typing import List, Optional
from fastapi.responses import JSONResponse
from sqlalchemy import text, or_, and_, desc
from datetime import datetime, timedelta

from src.schemas.anthropometrics import (
    AnthropometricsCreate, 
    AnthropometricsUpdate, 
    AnthropometricsResponse,
    AnthropometricsLock,
    AnthropometricsPost,
    AnthropometricsResponseMessage
)
from src.database.session import get_db
from src.models.anthropometrics import ClientAnthropometrics

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AnthropometricsResponseMessage)
async def create_anthropometrics(
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Create a new client anthropometrics record.
    
    - Expects a JSON body matching the AnthropometricsCreate schema
    - Generates OID automatically
    - Sets systemDate_dat to current timestamp
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
        for uuid_field in ["clientOID", "Rx_OID", "postedBy_GUID"]:
            if uuid_field in body and body[uuid_field]:
                body[uuid_field] = UUID(body[uuid_field])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid UUID format: {str(e)}"
        )

    # Generate OID
    body["OID"] = uuid4()
    
    # Set systemDate_dat to current timestamp
    body["systemDate_dat"] = datetime.utcnow()
    
    # Validate against AnthropometricsCreate schema
    try:
        anthropometrics_data = AnthropometricsCreate(**body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Validation error: {str(e)}"
        )

    # Check for existing record with same clientOID and date_dat
    existing_record = db.query(ClientAnthropometrics).filter(
        and_(
            ClientAnthropometrics.clientOID == anthropometrics_data.clientOID,
            ClientAnthropometrics.date_dat == anthropometrics_data.date_dat
        )
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Anthropometrics record already exists for this client and date"
        )

    # Create ClientAnthropometrics instance
    db_anthropometrics = ClientAnthropometrics(**body)

    # Insert record
    try:
        db.add(db_anthropometrics)
        db.commit()
        db.refresh(db_anthropometrics)
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
        "message": "Anthropometrics record created successfully", 
        "anthropometrics_id": str(db_anthropometrics.OID)
    }

@router.get("/{record_id}", response_model=AnthropometricsResponse)
async def get_anthropometrics(
    record_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Retrieve an anthropometrics record by its OID.
    
    - Returns the complete anthropometrics information
    - Raises 404 if record not found
    """
    db_record = db.query(ClientAnthropometrics).filter(ClientAnthropometrics.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Anthropometrics record with ID {record_id} not found"
        )
    return db_record

@router.get("/client/{client_id}", response_model=List[AnthropometricsResponse])
async def get_client_anthropometrics(
    client_id: UUID,
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all anthropometrics records for a specific client.
    
    - Supports pagination with skip/limit parameters
    - Can filter by date range with start_date and end_date
    - Returns records sorted by date (newest first)
    - Returns an empty list if no records found
    """
    query = db.query(ClientAnthropometrics).filter(ClientAnthropometrics.clientOID == client_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(ClientAnthropometrics.date_dat >= start_date)
    if end_date:
        query = query.filter(ClientAnthropometrics.date_dat <= end_date)
    
    # Sort by date (newest first)
    query = query.order_by(desc(ClientAnthropometrics.date_dat))
    
    # Apply pagination
    records = query.offset(skip).limit(limit).all()
    
    return records

@router.get("/client/{client_id}/latest", response_model=AnthropometricsResponse)
async def get_latest_anthropometrics(
    client_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve the most recent anthropometrics record for a specific client.
    
    - Returns the latest record based on date_dat
    - Raises 404 if no records found for the client
    """
    latest_record = db.query(ClientAnthropometrics).filter(
        ClientAnthropometrics.clientOID == client_id
    ).order_by(desc(ClientAnthropometrics.date_dat)).first()
    
    if not latest_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No anthropometrics records found for client {client_id}"
        )
    
    return latest_record

@router.put("/{record_id}", response_model=AnthropometricsResponseMessage)
async def update_anthropometrics(
    record_id: UUID, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update an existing anthropometrics record.
    
    - Requires record_id in the path
    - Expects a JSON body with fields to update
    - Cannot update locked records
    - Returns the updated record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAnthropometrics).filter(ClientAnthropometrics.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Anthropometrics record with ID {record_id} not found"
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
        for uuid_field in ["Rx_OID", "postedBy_GUID"]:
            if uuid_field in body and body[uuid_field]:
                body[uuid_field] = UUID(body[uuid_field])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid UUID format: {str(e)}"
        )
    
    # Prevent updating immutable fields
    immutable_fields = ["OID", "clientOID", "systemDate_dat", "createdBy_str"]
    for field in immutable_fields:
        if field in body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot update {field} field"
            )
    
    # Validate against AnthropometricsUpdate schema
    try:
        update_data = AnthropometricsUpdate(**body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=f"Validation error: {str(e)}"
        )
    
    # Update record attributes
    try:
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
        "message": "Anthropometrics record updated successfully", 
        "anthropometrics_id": str(db_record.OID)
    }

@router.delete("/{record_id}", response_model=AnthropometricsResponseMessage)
async def delete_anthropometrics(
    record_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Delete an anthropometrics record.
    
    - Requires record_id in the path
    - Cannot delete locked or posted records
    - Permanently removes the record from the database
    - Returns the deleted record's OID and a success message
    """
    # Check if record exists
    db_record = db.query(ClientAnthropometrics).filter(ClientAnthropometrics.OID == record_id).first()
    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Anthropometrics record with ID {record_id} not found"
        )
    
    # Check if record is locked
    if db_record.locked_bol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete a locked record"
        )
    
    # Check if record is posted
    if db_record.posted_bol:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete a posted record"
        )
    
    try:
        db.delete(db_record)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Anthropometrics record deleted successfully", 
        "anthropometrics_id": str(record_id)
    }

