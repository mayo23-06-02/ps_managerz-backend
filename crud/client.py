from sqlalchemy.orm import Session
from models.clients import Client
from schemas.client import ClientCreate
from uuid import UUID

def get_client_by_id(db: Session, client_id: UUID):
    return db.query(Client).filter(Client.clientID == client_id).first()

def create_client(db: Session, client: ClientCreate):
    db_client = Client(**client.dict(exclude={'clientID'}))
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client