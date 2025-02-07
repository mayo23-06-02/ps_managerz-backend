from sqlalchemy.orm import Session
from models.users import User
from schemas.user import UserCreate

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.userName_str == username).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict(exclude={'userID'}))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user