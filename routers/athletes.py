from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.database import get_db
from auth.dependencies import get_current_user
from models.user import User
from models.athlete import Athlete
from models.participant import Participant
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid
import datetime

router = APIRouter(prefix="/athletes", tags=["athletes"])


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    country: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    bodyweight_kg: Optional[Decimal] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    instagram: Optional[str] = None
    bio: Optional[str] = None
    achievements: Optional[str] = None


class AthleteResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    country: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[datetime.date]
    bodyweight_kg: Optional[Decimal] = None
    email: Optional[str]

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    athlete_id: uuid.UUID
    competition_division_id: uuid.UUID
    bib_no: Optional[int] = None
    bodyweight_kg: Optional[Decimal] = None


class ParticipantResponse(BaseModel):
    id: uuid.UUID
    athlete_id: uuid.UUID
    competition_division_id: uuid.UUID
    bib_no: Optional[int]
    bodyweight_kg: Optional[Decimal]
    first_name: str
    last_name: str
    country: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[datetime.date]

    class Config:
        from_attributes = True


@router.get("/search", response_model=list[AthleteResponse])
async def search_athletes(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Athlete).where(
            or_(
                Athlete.first_name.ilike(f'%{q}%'),
                Athlete.last_name.ilike(f'%{q}%'),
            )
        ).limit(10)
    )
    return result.scalars().all()


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(athlete_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete



@router.get("/", response_model=list[AthleteResponse])
async def list_athletes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Athlete).order_by(Athlete.last_name))
    return result.scalars().all()


@router.post("/", response_model=AthleteResponse)
async def create_athlete(data: AthleteCreate, db: AsyncSession = Depends(get_db)):
    athlete = Athlete(
        id=uuid.uuid4(),
        first_name=data.first_name,
        last_name=data.last_name,
        country=data.country,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        email=data.email,
        phone=data.phone,
    )
    db.add(athlete)
    await db.commit()
    await db.refresh(athlete)
    return athlete


@router.get("/division/{division_id}", response_model=list[ParticipantResponse])
async def list_participants(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Participant)
        .where(Participant.competition_division_id == division_id)
        .options(selectinload(Participant.athlete))
        .order_by(Participant.bib_no)
    )
    participants = result.scalars().all()
    return [
        ParticipantResponse(
            id=p.id,
            athlete_id=p.athlete_id,
            competition_division_id=p.competition_division_id,
            bib_no=p.bib_no,
            bodyweight_kg=p.bodyweight_kg,
            first_name=p.athlete.first_name,
            last_name=p.athlete.last_name,
            country=p.athlete.country,
            gender=p.athlete.gender,
            date_of_birth=p.athlete.date_of_birth,
        )
        for p in participants
    ]


@router.post("/register", response_model=ParticipantResponse)
async def register_participant(data: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Participant).where(
            Participant.athlete_id == data.athlete_id,
            Participant.competition_division_id == data.competition_division_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Athlete already registered in this division")

    participant = Participant(
        id=uuid.uuid4(),
        athlete_id=data.athlete_id,
        competition_division_id=data.competition_division_id,
        bib_no=data.bib_no,
        bodyweight_kg=data.bodyweight_kg,
    )
    db.add(participant)
    await db.commit()

    athlete = await db.get(Athlete, data.athlete_id)
    return ParticipantResponse(
        id=participant.id,
        athlete_id=participant.athlete_id,
        competition_division_id=participant.competition_division_id,
        bib_no=participant.bib_no,
        bodyweight_kg=participant.bodyweight_kg,
        first_name=athlete.first_name,
        last_name=athlete.last_name,
        country=athlete.country,
        gender=athlete.gender,
        date_of_birth=athlete.date_of_birth,
    )


@router.delete("/participants/{participant_id}")
async def remove_participant(participant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    p = await db.get(Participant, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    await db.delete(p)
    await db.commit()
    return {"status": "ok"}


import shutil, os
from fastapi import UploadFile, File
from pathlib import Path

UPLOAD_DIR = Path("uploads/athletes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{athlete_id}/photo")
async def upload_photo(
    athlete_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    if current_user.athlete_id != athlete_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    filename = f"athletes/{athlete_id}.{ext}"
    file_bytes = await file.read()
    from utils.r2 import upload_file_to_r2
    upload_file_to_r2(file_bytes, filename, file.content_type or "image/jpeg")
    photo_url = f"https://pub-22fdd3117dc246539752f3a04b02035f.r2.dev/uploads/{filename}"
    athlete.photo_url = photo_url
    await db.commit()

    return {"photo_url": photo_url}


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(athlete_id: uuid.UUID, data: AthleteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    if current_user.athlete_id != athlete_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    await db.commit()
    await db.refresh(athlete)
    return athlete


import shutil, os


# ── SPONSORS ──────────────────────────────────────────────────────────────────
from models.athlete_sponsor import AthleteSponsor

class SponsorCreate(BaseModel):
    name: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None

class SponsorResponse(BaseModel):
    id: uuid.UUID
    athlete_id: uuid.UUID
    name: str
    logo_url: Optional[str]
    website_url: Optional[str]
    tier: Optional[str]

    class Config:
        from_attributes = True


@router.get("/{athlete_id}/sponsors", response_model=list[SponsorResponse])
async def get_sponsors(athlete_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AthleteSponsor).where(AthleteSponsor.athlete_id == athlete_id)
    )
    return result.scalars().all()


@router.post("/{athlete_id}/sponsors", response_model=SponsorResponse)
async def add_sponsor(athlete_id: uuid.UUID, data: SponsorCreate, db: AsyncSession = Depends(get_db)):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    count = await db.execute(
        select(AthleteSponsor).where(
            AthleteSponsor.athlete_id == athlete_id,
            AthleteSponsor.tier == "free"
        )
    )
    if len(count.scalars().all()) >= 3:
        raise HTTPException(status_code=400, detail="Free tier limit: max 3 sponsors")

    sponsor = AthleteSponsor(
        id=uuid.uuid4(),
        athlete_id=athlete_id,
        name=data.name,
        logo_url=data.logo_url,
        website_url=data.website_url,
        tier="free",
    )
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    return sponsor


@router.delete("/{athlete_id}/sponsors/{sponsor_id}")
async def remove_sponsor(athlete_id: uuid.UUID, sponsor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    sponsor = await db.get(AthleteSponsor, sponsor_id)
    if not sponsor or sponsor.athlete_id != athlete_id:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    await db.delete(sponsor)
    await db.commit()
    return {"status": "ok"}


@router.post("/{athlete_id}/sponsors/{sponsor_id}/logo")
async def upload_sponsor_logo(
    athlete_id: uuid.UUID,
    sponsor_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.athlete_id != athlete_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    sponsor = await db.get(AthleteSponsor, sponsor_id)
    if not sponsor or sponsor.athlete_id != athlete_id:
        raise HTTPException(status_code=404, detail="Sponsor not found")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    logo_dir = Path("uploads/sponsors")
    logo_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{sponsor_id}.{ext}"
    filepath = logo_dir / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    sponsor.logo_url = f"/uploads/sponsors/{filename}"
    await db.commit()

    return {"logo_url": sponsor.logo_url}

@router.get("/{athlete_id}/data")
async def get_athlete_data(athlete_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.athlete import Athlete
    a = await db.get(Athlete, athlete_id)
    if not a:
        raise HTTPException(404)
    return {
        "id": str(a.id),
        "first_name": a.first_name,
        "last_name": a.last_name,
        "country": a.country,
        "gender": getattr(a, 'gender', None),
        "date_of_birth": str(a.date_of_birth) if getattr(a, 'date_of_birth', None) else None,
        "bodyweight_kg": str(a.bodyweight_kg) if getattr(a, 'bodyweight_kg', None) else None,
        "phone": getattr(a, 'phone', None),
        "instagram": getattr(a, 'instagram', None),
        "photo_url": getattr(a, 'photo_url', None),
        "bio": getattr(a, 'bio', None),
        "achievements": getattr(a, 'achievements', None),
    }
