import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from schemas.antropometrics import ClientAntropometricCreate, ClientAntropometricGetAll
from models.antropometrics import ClientAntropometric
from api.deps import get_db
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client_antropometric(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    try:
        antropometric = ClientAntropometricCreate(**body)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db_antropometric = ClientAntropometric(**antropometric.dict())
    db.add(db_antropometric)
    db.commit()
    db.refresh(db_antropometric)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Client anthropometric created successfully", "antropometric": str(db_antropometric.OID)})

@router.get("/", response_model=List[ClientAntropometricGetAll])
async def read_client_antropometrics(db: Session = Depends(get_db)):
    antropometrics = db.query(ClientAntropometric).all()
    return [ClientAntropometricGetAll.from_orm(antropometric) for antropometric in antropometrics]

@router.get("/{clientOID}", response_model=List[ClientAntropometricGetAll])
async def read_client_antropometrics_by_client_oid(clientOID: UUID, db: Session = Depends(get_db)):
    antropometrics = db.query(ClientAntropometric).filter(ClientAntropometric.clientOID == clientOID).all()
    if not antropometrics:
        raise HTTPException(status_code=404, detail="Client anthropometrics not found")
    return [ClientAntropometricGetAll.from_orm(antropometric) for antropometric in antropometrics]