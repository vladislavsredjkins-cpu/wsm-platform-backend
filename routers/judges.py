from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.database import get_db
from models.judge import Judge
from models.judge_certificate import JudgeCertificate
from models.judge_competition import JudgeCompetition
from models.judge_levels import JudgeLevel, JUDGE_LEVEL_LABELS
from auth.dependencies import get_current_user
from models.user import User
from pydantic import BaseModel
from typing import Optional
import uuid, datetime, shutil
from pathlib import Path

router = APIRouter(prefix="/judges", tags=["judges"])

UPLOAD_DIR = Path("uploads/judges")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

CERT_DIR = Path("uploads/certificates")
CERT_DIR.mkdir(parents=True, exist_ok=True)


class JudgeCreate(BaseModel):
    first_name: str
    last_name: str
    country: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    level: Optional[JudgeLevel] = None
    instagram: Optional[str] = None

class JudgeResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    country: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[datetime.date]
    email: Optional[str]
    photo_url: Optional[str]
    level: Optional[str]
    level_label: Optional[str] = None

    class Config:
        from_attributes = True

class CertificateCreate(BaseModel):
    title: str
    issued_by: Optional[str] = None
    issued_date: Optional[datetime.date] = None
    expires_date: Optional[datetime.date] = None

class CertificateResponse(BaseModel):
    id: uuid.UUID
    judge_id: uuid.UUID
    title: str
    issued_by: Optional[str]
    issued_date: Optional[datetime.date]
    expires_date: Optional[datetime.date]
    file_url: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[JudgeResponse])
async def list_judges(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Judge).order_by(Judge.last_name))
    judges = result.scalars().all()
    out = []
    for j in judges:
        jr = JudgeResponse.model_validate(j)
        jr.level_label = JUDGE_LEVEL_LABELS.get(JudgeLevel(j.level)) if j.level else None
        out.append(jr)
    return out




@router.get("/search")
async def search_judges(q: str = "", db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select, or_
    from models.judge import Judge
    result = await db.execute(
        select(Judge).where(
            or_(
                Judge.first_name.ilike(f"%{q}%"),
                Judge.last_name.ilike(f"%{q}%"),
                Judge.email.ilike(f"%{q}%"),
            )
        ).limit(10)
    )
    judges = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "first_name": j.first_name,
            "last_name": j.last_name,
            "country": j.country,
            "license_number": j.level,
        }
        for j in judges
    ]

@router.get("/{judge_id}", response_model=JudgeResponse)
async def get_judge(judge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    judge = await db.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    jr = JudgeResponse.model_validate(judge)
    jr.level_label = JUDGE_LEVEL_LABELS.get(JudgeLevel(judge.level)) if judge.level else None
    return jr


@router.post("/", response_model=JudgeResponse)
async def create_judge(data: JudgeCreate, db: AsyncSession = Depends(get_db)):
    judge = Judge(id=uuid.uuid4(), **data.model_dump())
    db.add(judge)
    await db.commit()
    await db.refresh(judge)
    return judge


@router.patch("/{judge_id}", response_model=JudgeResponse)
async def update_judge(
    judge_id: uuid.UUID,
    data: JudgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    judge = await db.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    if judge.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(judge, field, value)
    await db.commit()
    await db.refresh(judge)
    return judge


@router.post("/{judge_id}/photo")
async def upload_photo(
    judge_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    judge = await db.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    if judge.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    filename = f"{judge_id}.{ext}"
    with open(UPLOAD_DIR / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    judge.photo_url = f"/uploads/judges/{filename}"
    await db.commit()
    return {"photo_url": judge.photo_url}


@router.get("/{judge_id}/certificates", response_model=list[CertificateResponse])
async def list_certificates(judge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(JudgeCertificate).where(JudgeCertificate.judge_id == judge_id)
    )
    return result.scalars().all()


@router.post("/{judge_id}/certificates", response_model=CertificateResponse)
async def add_certificate(
    judge_id: uuid.UUID,
    data: CertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    judge = await db.get(Judge, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    if judge.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    cert = JudgeCertificate(id=uuid.uuid4(), judge_id=judge_id, **data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert


@router.post("/{judge_id}/certificates/{cert_id}/upload")
async def upload_certificate_file(
    judge_id: uuid.UUID,
    cert_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cert = await db.get(JudgeCertificate, cert_id)
    if not cert or cert.judge_id != judge_id:
        raise HTTPException(status_code=404, detail="Certificate not found")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp", "pdf"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/pdf allowed")

    filename = f"{cert_id}.{ext}"
    with open(CERT_DIR / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    cert.file_url = f"/uploads/certificates/{filename}"
    await db.commit()
    return {"file_url": cert.file_url}


@router.delete("/{judge_id}/certificates/{cert_id}")
async def delete_certificate(
    judge_id: uuid.UUID,
    cert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cert = await db.get(JudgeCertificate, cert_id)
    if not cert or cert.judge_id != judge_id:
        raise HTTPException(status_code=404, detail="Certificate not found")
    await db.delete(cert)
    await db.commit()
    return {"status": "ok"}


@router.get("/{judge_id}/data")
async def get_judge_profile_json(judge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.judge import Judge
    from models.user import User
    from sqlalchemy import select
    
    result = await db.execute(select(Judge).where(Judge.id == judge_id))
    judge = result.scalar_one_or_none()
    if not judge:
        raise HTTPException(404, "Judge not found")
    
    return {
        "id": str(judge.id),
        "first_name": judge.first_name,
        "last_name": judge.last_name,
        "country": judge.country,
        "level": judge.level,
        "photo_url": judge.photo_url,
        "instagram": judge.instagram,
        "phone": judge.phone,
        "gender": judge.gender,
        "date_of_birth": str(judge.date_of_birth) if judge.date_of_birth else None,
        "bio": getattr(judge, 'bio', None),
        "certificates": [],
        "competitions_judged": 0,
    }
