from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from db.database import get_db
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
    email: Optional[str] = None
    phone: Optional[str] = None


class AthleteResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    country: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[datetime.date]
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
    db: AsyncSession = Depends(get_db)
):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    filename = f"{athlete_id}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    photo_url = f"/uploads/athletes/{filename}"
    athlete.photo_url = photo_url
    await db.commit()

    return {"photo_url": photo_url}


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(athlete_id: uuid.UUID, data: AthleteCreate, db: AsyncSession = Depends(get_db)):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    await db.commit()
    await db.refresh(athlete)
    return athlete


import shutil, os
from fastapi import UploadFile, File
from pathlib import Path

UPLOAD_DIR = Path("uploads/athletes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/{athlete_id}/photo")
async def upload_photo(
    athlete_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    filename = f"{athlete_id}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    photo_url = f"/uploads/athletes/{filename}"
    athlete.photo_url = photo_url
    await db.commit()

    return {"photo_url": photo_url}


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(athlete_id: uuid.UUID, data: AthleteCreate, db: AsyncSession = Depends(get_db)):
    athlete = await db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    await db.commit()
    await db.refresh(athlete)
    return athlete
