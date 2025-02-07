from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from api.deps import get_db, get_current_user
from models.users import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LogoutRequest(BaseModel):
    userID: str

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: LogoutRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Invalidate the token by removing it from the client side
    # Since JWT tokens are stateless, we cannot invalidate them on the server side
    if str(current_user.userID) != request.userID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID does not match the current user",
        )
    return {"message": "Successfully logged out"}