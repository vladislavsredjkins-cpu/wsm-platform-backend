from datetime import date
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.database import SessionLocal
from models.competition import Competition


router = APIRouter(prefix="/competitions", tags=["competitions"])


class CompetitionCreate(BaseModel):
    name: str
    date_start: date
    date_end: date | None = None
    city: str | None = None
    country: str | None = None
    coefficient_q: float = Field(1.0, ge=0.1, le=10.0)


class CompetitionOut(CompetitionCreate):
    id: UUID

    class Config:
        from_attributes = True


@router.post("", response_model=CompetitionOut)
async def create_competition(payload: CompetitionCreate):
    async with SessionLocal() as session:
        competition = Competition(**payload.model_dump())
        session.add(competition)
        await session.commit()
        await session.refresh(competition)
        return competition


@router.get("", response_model=list[CompetitionOut])
async def list_competitions():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Competition).order_by(Competition.date_start.desc())
        )
        return list(result.scalars().all())
