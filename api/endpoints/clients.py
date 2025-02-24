from fastapi import APIRouter, Depends, HTTPException, status, Request
import json
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from schemas.client import ClientCreate, ClientGetAll
from api.deps import get_db
from models.clients import Client as DBClient
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client_endpoint(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    print(json.dumps(body, indent=4))  # Debugging: Print the incoming request data

    # Convert string UUIDs to UUID
    if 'customerOID' in body and body['customerOID']:
        body['customerOID'] = UUID(body['customerOID'])
    if 'entryServicePointOID' in body and body['entryServicePointOID']:
        body['entryServicePointOID'] = UUID(body['entryServicePointOID'])

    # Check for existing client with the same systemKey_str
    existing_client = db.query(DBClient).filter(DBClient.systemKey_str == body['systemKey_str']).first()
    if existing_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client with this system key already exists")

    try:
        client = ClientCreate(**body)
    except Exception as e:
        print(f"Error creating ClientCreate object: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Ensure OID is unique
    if 'OID' not in body or not body['OID']:
        body['OID'] = str(uuid4())
    else:
        existing_oid_client = db.query(DBClient).filter(DBClient.OID == body['OID']).first()
        if existing_oid_client:
            body['OID'] = str(uuid4())

    try:
        db_client = DBClient(**client.dict(exclude={'OID'}), OID=body['OID'])  # Include OID in the insert statement
    except Exception as e:
        print(f"Error creating DBClient object: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        # Set IDENTITY_INSERT to ON
        db.execute(text("SET IDENTITY_INSERT tbClients ON"))
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
    except Exception as e:
        print(f"Error during database operations: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed")
    finally:
        # Ensure IDENTITY_INSERT is set to OFF
        db.execute(text("SET IDENTITY_INSERT tbClients OFF"))

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Client created successfully", "client": str(db_client.OID)})

@router.get("/national-id/{nationalIdNumber}", response_model=ClientGetAll)
async def read_client(nationalIdNumber: str, db: Session = Depends(get_db)):
    db_client = db.query(DBClient).filter(DBClient.nationalIdNumber_str == nationalIdNumber).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientGetAll.from_orm(db_client)

@router.get("/", response_model=List[ClientGetAll])
async def read_clients(db: Session = Depends(get_db)):
    clients = db.query(DBClient).all()
    return [ClientGetAll.from_orm(client) for client in clients]