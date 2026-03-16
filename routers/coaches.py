import uuid, os, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import date
from db.database import get_db
from models.coach import Coach
from models.coach_certificate import CoachCertificate
from auth.dependencies import get_current_user

router = APIRouter(prefix="/coaches", tags=["coaches"])

class CoachCreate(BaseModel):
    first_name: str
    last_name: str
    country: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None
    level: Optional[str] = None  # COACH_1 / COACH_2 / COACH_3

class CoachUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None
    level: Optional[str] = None

class CertCreate(BaseModel):
    title: str
    issued_by: Optional[str] = None
    issued_date: Optional[date] = None
    expires_date: Optional[date] = None

@router.get("/")
async def list_coaches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coach).order_by(Coach.last_name))
    coaches = result.scalars().all()
    return coaches

@router.get("/{coach_id}")
async def get_coach(coach_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach

@router.post("/")
async def create_coach(data: CoachCreate, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    coach = Coach(**data.dict())
    db.add(coach)
    await db.commit()
    await db.refresh(coach)
    return coach

@router.patch("/{coach_id}")
async def update_coach(coach_id: uuid.UUID, data: CoachUpdate,
                       db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    for k, v in data.dict(exclude_none=True).items():
        setattr(coach, k, v)
    await db.commit()
    await db.refresh(coach)
    return coach

@router.post("/{coach_id}/photo")
async def upload_photo(coach_id: uuid.UUID, file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    os.makedirs("uploads/coaches", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"uploads/coaches/{coach_id}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    coach.photo_url = f"/{filename}"
    await db.commit()
    return {"photo_url": coach.photo_url}

@router.get("/{coach_id}/certificates")
async def list_certificates(coach_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CoachCertificate).where(CoachCertificate.coach_id == coach_id)
    )
    return result.scalars().all()

@router.post("/{coach_id}/certificates")
async def add_certificate(coach_id: uuid.UUID, data: CertCreate,
                          db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    coach = await db.get(Coach, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    cert = CoachCertificate(coach_id=coach_id, **data.dict())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert

@router.post("/{coach_id}/certificates/{cert_id}/file")
async def upload_cert_file(coach_id: uuid.UUID, cert_id: uuid.UUID,
                           file: UploadFile = File(...),
                           db: AsyncSession = Depends(get_db),
                           current_user=Depends(get_current_user)):
    cert = await db.get(CoachCertificate, cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    os.makedirs("uploads/coach_certificates", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"uploads/coach_certificates/{cert_id}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    cert.file_url = f"/{filename}"
    await db.commit()
    return {"file_url": cert.file_url}

@router.delete("/{coach_id}/certificates/{cert_id}")
async def delete_certificate(coach_id: uuid.UUID, cert_id: uuid.UUID,
                              db: AsyncSession = Depends(get_db),
                              current_user=Depends(get_current_user)):
    cert = await db.get(CoachCertificate, cert_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    await db.delete(cert)
    await db.commit()
    return {"status": "deleted"}

@router.get("/{coach_id}/data")
async def get_coach_data(coach_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.coach import Coach
    co = await db.get(Coach, coach_id)
    if not co:
        raise HTTPException(404)
    return {
        "id": str(co.id),
        "first_name": co.first_name,
        "last_name": co.last_name,
        "country": getattr(co, 'country', None),
        "phone": getattr(co, 'phone', None),
        "instagram": getattr(co, 'instagram', None),
        "photo_url": getattr(co, 'photo_url', None),
        "bio": getattr(co, 'bio', None),
        "level": getattr(co, 'level', None),
    }
