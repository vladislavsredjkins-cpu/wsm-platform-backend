from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.user import User
from models.athlete import Athlete
from auth.security import hash_password, verify_password, create_access_token
from auth.dependencies import get_current_user
from pydantic import BaseModel
import datetime
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str
    athlete_id: str | None = None

class LinkAthleteRequest(BaseModel):
    athlete_id: uuid.UUID

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=user.id, email=user.email, role=user.role)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token, user_id=user.id,
        email=user.email, role=user.role,
        athlete_id=str(user.athlete_id) if user.athlete_id else None
    )

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "athlete_id": str(current_user.athlete_id) if current_user.athlete_id else None,
        "is_active": current_user.is_active,
    }

@router.post("/link-athlete")
async def link_athlete(
    data: LinkAthleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    athlete = await db.get(Athlete, data.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    current_user.athlete_id = data.athlete_id
    await db.commit()
    return {"status": "ok", "athlete_id": str(data.athlete_id)}
