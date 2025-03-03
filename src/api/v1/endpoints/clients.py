# src/api/v1/endpoints/clients.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from typing import List, Optional
from fastapi.responses import JSONResponse
from sqlalchemy import text
from datetime import datetime

from src.schemas.client import ClientCreate, ClientUpdate, ClientGetAll
from src.database.session import get_db
from src.models.client import Client as DBClient

router = APIRouter()

# CREATE
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_client(request: Request, db: Session = Depends(get_db)):
    """
    Create a new client in tbClients.
    Expects a JSON body matching the ClientCreate schema.
    If OID is not provided, generates a new UUID.
    Returns a success message with the created client's OID.
    """
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    # Convert string UUIDs to UUID objects if present
    try:
        if "OID" in body and body["OID"]:
            body["OID"] = UUID(body["OID"])
        if "customerOID" in body and body["customerOID"]:
            body["customerOID"] = UUID(body["customerOID"])
        if "entryServicePointOID" in body and body["entryServicePointOID"]:
            body["entryServicePointOID"] = UUID(body["entryServicePointOID"])
        if "extSysOID_ART" in body and body["extSysOID_ART"]:
            body["extSysOID_ART"] = UUID(body["extSysOID_ART"])
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid UUID format: {str(e)}")

    # Validate against ClientCreate schema
    try:
        client = ClientCreate(**body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Validation error: {str(e)}")

    # Check for existing client by registrationNo_str
    existing_client = db.query(DBClient).filter(DBClient.registrationNo_str == client.registrationNo_str).first()
    if existing_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client with this registration number already exists")

    # Ensure OID is unique and provided
    if "OID" not in body or not body["OID"]:
        body["OID"] = uuid4()  # Generate new UUID if not provided
    else:
        existing_oid_client = db.query(DBClient).filter(DBClient.OID == body["OID"]).first()
        if existing_oid_client:
            body["OID"] = uuid4()  # Generate new UUID if provided OID already exists

    # Create DBClient instance with OID
    db_client_data = client.dict(exclude={"OID"})
    db_client = DBClient(**db_client_data, OID=body["OID"])

    # Insert with IDENTITY_INSERT ON
    try:
        db.execute(text("SET IDENTITY_INSERT tbClients ON"))
        db.add(db_client)
        db.commit()
        db.execute(text("SET IDENTITY_INSERT tbClients OFF"))
        db.refresh(db_client)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    finally:
        db.execute(text("SET IDENTITY_INSERT tbClients OFF"))
        db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Client created successfully", "client": str(db_client.OID)}
    )

# READ (Single by customerID or nationalIdNumber_str)
@router.get("/single/", response_model=ClientGetAll)
async def read_client(
    customer_id: Optional[int] = None,
    national_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a client by their customerID (int) or nationalIdNumber_str (string).
    At least one parameter must be provided.
    """
    if not customer_id and not national_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either customerID or nationalIdNumber_str")

    query = db.query(DBClient)
    if customer_id:
        db_client = query.filter(DBClient.customerID == customer_id).first()
    else:
        db_client = query.filter(DBClient.nationalIdNumber_str == national_id).first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientGetAll.from_orm(db_client)

# READ (All)
@router.get("/", response_model=List[ClientGetAll])
async def read_clients(db: Session = Depends(get_db)):
    """
    Retrieve all clients.
    """
    clients = db.query(DBClient).all()
    if not clients:
        return []
    return [ClientGetAll.from_orm(client) for client in clients]

# UPDATE (by customerID or nationalIdNumber_str)
@router.put("/single/", response_model=ClientGetAll)
async def update_client(
    customer_id: Optional[int] = None,
    national_id: Optional[str] = None,
    client_update: ClientUpdate = Depends(),
    db: Session = Depends(get_db)
):
    """
    Update an existing client by their customerID (int) or nationalIdNumber_str (string).
    Expects a JSON body matching the ClientUpdate schema (partial updates allowed).
    """
    if not customer_id and not national_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either customerID or nationalIdNumber_str")

    query = db.query(DBClient)
    if customer_id:
        db_client = query.filter(DBClient.customerID == customer_id).first()
    else:
        db_client = query.filter(DBClient.nationalIdNumber_str == national_id).first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    update_data = client_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)

    try:
        db.commit()
        db.refresh(db_client)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return ClientGetAll.from_orm(db_client)

# DELETE (Soft Delete by customerID or nationalIdNumber_str)
@router.delete("/single/", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_client(
    customer_id: Optional[int] = None,
    national_id: Optional[str] = None,
    deleted_by: str = "system",
    reason: str = "Requested by user",
    db: Session = Depends(get_db)
):
    """
    Soft delete a client by their customerID (int) or nationalIdNumber_str (string).
    Sets deleted_bol to True with deletion details.
    """
    if not customer_id and not national_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either customerID or nationalIdNumber_str")

    query = db.query(DBClient)
    if customer_id:
        db_client = query.filter(DBClient.customerID == customer_id).first()
    else:
        db_client = query.filter(DBClient.nationalIdNumber_str == national_id).first()

    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if db_client.deleted_bol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client already deleted")

    try:
        db_client.deleted_bol = True
        db_client.deletedBy_str = deleted_by
        db_client.deletetedReason_str = reason
        db_client.deletedDate_dat = datetime.utcnow()
        db.commit()
        db.refresh(db_client)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Client deleted successfully", "client": str(db_client.OID)}
    )