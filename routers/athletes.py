from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.athlete import Athlete
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

router = APIRouter(prefix="/athletes", tags=["athletes"])


class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    country_code: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    gender: Optional[str] = None
    is_para: bool = False
    para_class: Optional[str] = None


class AthleteResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    country_code: Optional[str]
    birth_date: Optional[datetime.date]
    gender: Optional[str]
    is_para: bool
    para_class: Optional[str]
    certification_status: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=AthleteResponse)
async def create_athlete(data: AthleteCreate, db: AsyncSession = Depends(get_db)):
    athlete = Athlete(
        id=uuid.uuid4(),
        first_name=data.first_name,
        last_name=data.last_name,
        country_code=data.country_code,
        birth_date=data.birth_date,
        gender=data.gender,
        is_para=data.is_para,
        para_class=data.para_class,
        certification_status="PENDING",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(athlete)
    await db.commit()
    await db.refresh(athlete)
    return athlete


@router.get("/", response_model=list[AthleteResponse])
async def list_athletes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Athlete).order_by(Athlete.last_name))
    return result.scalars().all()


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(athlete_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Athlete).where(Athlete.id == athlete_id))
    athlete = result.scalar_one_or_none()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return athlete