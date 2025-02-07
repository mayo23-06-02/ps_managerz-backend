from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from api.deps import get_db
from models.users import User
from utils.otp import generate_otp, verify_otp
from utils.email import send_otp_email

router = APIRouter()

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email_str == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    otp = generate_otp(request.email)
    send_otp_email(request.email, otp)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp_endpoint(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    if verify_otp(request.email, request.otp):
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")