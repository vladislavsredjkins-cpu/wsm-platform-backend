from datetime import datetime
from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from db.database import SessionLocal
from models.competition import Competition
from models.competition_division import CompetitionDivision


router = APIRouter(tags=["divisions"])


DivisionKey = Literal["MEN", "WOMEN", "PARA"]
CompetitionFormat = Literal["CLASSIC", "PARA", "RELAY", "TEAM_BATTLE"]
LifecycleStatus = Literal["DRAFT", "SUBMITTED", "APPROVED", "LIVE", "RESULTS_VALIDATED", "LOCKED"]


class DivisionCreate(BaseModel):
    division_key: DivisionKey
    format: CompetitionFormat
    status: LifecycleStatus = "DRAFT"


class DivisionOut(DivisionCreate):
    id: UUID
    competition_id: UUID
    approved_at: datetime | None = None
    live_at: datetime | None = None
    locked_at: datetime | None = None

    class Config:
        from_attributes = True


@router.post("/competitions/{competition_id}/divisions", response_model=DivisionOut)
async def create_division(competition_id: UUID, payload: DivisionCreate):
    async with SessionLocal() as session:
        competition = await session.get(Competition, competition_id)
        if not competition:
            raise HTTPException(status_code=404, detail="Competition not found")

        try:
            division = CompetitionDivision(
                competition_id=competition_id,
                division_key=payload.division_key,
                format=payload.format,
                status=payload.status,
            )
            session.add(division)
            await session.commit()
            await session.refresh(division)
            return division

        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitions/{competition_id}/divisions", response_model=list[DivisionOut])
async def list_divisions(competition_id: UUID):
    async with SessionLocal() as session:
        result = await session.execute(
            select(CompetitionDivision).where(
                CompetitionDivision.competition_id == competition_id
            )
        )
        return list(result.scalars().all())
