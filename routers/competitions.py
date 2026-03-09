from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition import Competition
from auth.dependencies import require_organizer
from models.user import User
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

router = APIRouter(prefix="/competitions", tags=["competitions"])


class CompetitionCreate(BaseModel):
    name: str
    date_start: Optional[datetime.date] = None
    date_end: Optional[datetime.date] = None
    city: Optional[str] = None
    country: Optional[str] = None
    coefficient_q: float = 1.0
    season_id: Optional[uuid.UUID] = None


class CompetitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    date_start: Optional[datetime.date]
    date_end: Optional[datetime.date]
    city: Optional[str]
    country: Optional[str]
    coefficient_q: float

    class Config:
        from_attributes = True


@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    data: CompetitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    competition = Competition(
        id=uuid.uuid4(),
        name=data.name,
        date_start=data.date_start,
        date_end=data.date_end,
        city=data.city,
        country=data.country,
        coefficient_q=data.coefficient_q,
        season_id=data.season_id,
    )
    db.add(competition)
    await db.commit()
    await db.refresh(competition)
    return competition


@router.get("/", response_model=list[CompetitionResponse])
async def list_competitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).order_by(Competition.date_start.desc()))
    return result.scalars().all()


@router.get("/{competition_id}", response_model=CompetitionResponse)
async def get_competition(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition