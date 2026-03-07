from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.database import SessionLocal
from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision


router = APIRouter(tags=["disciplines"])


DisciplineMode = Literal[
    "TIME_WITH_DISTANCE_FALLBACK",
    "AMRAP_REPS",
    "AMRAP_DISTANCE",
    "MAX_WEIGHT_WITHIN_CAP",
    "RELAY_DUAL_METRIC",
]


class DisciplineCreate(BaseModel):
    order_no: int = Field(..., ge=1, le=50)
    discipline_name: str
    discipline_mode: DisciplineMode
    time_cap_seconds: int | None = Field(None, ge=1, le=3600)
    lanes_per_heat: int | None = Field(None, ge=1, le=20)
    track_length_meters: int | None = Field(None, ge=1, le=10000)


class DisciplineOut(DisciplineCreate):
    id: UUID
    competition_division_id: UUID

    class Config:
        from_attributes = True


@router.post("/divisions/{division_id}/disciplines", response_model=DisciplineOut)
async def create_discipline(division_id: UUID, payload: DisciplineCreate):
    async with SessionLocal() as session:
        division = await session.get(CompetitionDivision, division_id)
        if not division:
            raise HTTPException(status_code=404, detail="Division not found")

        try:
            discipline = CompetitionDiscipline(
                competition_division_id=division_id,
                order_no=payload.order_no,
                discipline_name=payload.discipline_name,
                discipline_mode=payload.discipline_mode,
                time_cap_seconds=payload.time_cap_seconds,
                lanes_per_heat=payload.lanes_per_heat,
                track_length_meters=payload.track_length_meters,
            )
            session.add(discipline)
            await session.commit()
            await session.refresh(discipline)
            return discipline

        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/divisions/{division_id}/disciplines", response_model=list[DisciplineOut])
async def list_disciplines(division_id: UUID):
    async with SessionLocal() as session:
        result = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        return list(result.scalars().all())
