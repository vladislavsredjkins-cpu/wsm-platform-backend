from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition import Competition
from models.season import Season
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid
import datetime

router = APIRouter(prefix="/competitions", tags=["competitions"])

COMPETITION_TYPES = {
    "WORLD_CHAMPIONSHIP": Decimal("10"),
    "CONTINENTAL_CHAMPIONSHIP": Decimal("6"),
    "WORLD_CUP": Decimal("4"),
    "SUBCONTINENTAL": Decimal("2"),
    "NATIONAL_CHAMPIONSHIP": Decimal("1"),
    "INTERNATIONAL_TOURNAMENT": Decimal("0.5"),
}


class CompetitionCreate(BaseModel):
    name: str
    competition_type: str
    track_type: str
    country_code: Optional[str] = None
    city: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    season_id: Optional[uuid.UUID] = None


class CompetitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    competition_type: str
    track_type: str
    q_coefficient: Decimal
    country_code: Optional[str]
    city: Optional[str]
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    status: str

    class Config:
        from_attributes = True


@router.post("/", response_model=CompetitionResponse)
async def create_competition(data: CompetitionCreate, db: AsyncSession = Depends(get_db)):
    q = COMPETITION_TYPES.get(data.competition_type)
    if not q:
        raise HTTPException(status_code=400, detail=f"Unknown competition_type. Valid: {list(COMPETITION_TYPES.keys())}")

    competition = Competition(
        id=uuid.uuid4(),
        name=data.name,
        competition_type=data.competition_type,
        track_type=data.track_type,
        q_coefficient=q,
        country_code=data.country_code,
        city=data.city,
        start_date=data.start_date,
        end_date=data.end_date,
        season_id=data.season_id,
        status="DRAFT",
        created_at=datetime.datetime.utcnow(),
    )
    db.add(competition)
    await db.commit()
    await db.refresh(competition)
    return competition


@router.get("/", response_model=list[CompetitionResponse])
async def list_competitions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).order_by(Competition.created_at.desc()))
    return result.scalars().all()


@router.get("/{competition_id}", response_model=CompetitionResponse)
async def get_competition(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition