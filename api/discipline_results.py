from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from db.database import SessionLocal
from models.competition_discipline import CompetitionDiscipline
from models.discipline_result import DisciplineResult
from models.participant import Participant


router = APIRouter(tags=["discipline_results"])


StatusFlag = Literal["OK", "DNF", "DQ", "DNS"]


class DisciplineResultCreate(BaseModel):
    athlete_id: UUID
    primary_value: float | None = None
    secondary_value: float | None = None
    status_flag: StatusFlag = "OK"


class DisciplineResultOut(DisciplineResultCreate):
    id: UUID
    competition_discipline_id: UUID
    participant_id: UUID

    class Config:
        from_attributes = True


@router.post("/disciplines/{competition_discipline_id}/results", response_model=DisciplineResultOut)
async def upsert_discipline_result(
    competition_discipline_id: UUID, payload: DisciplineResultCreate
):
    async with SessionLocal() as session:
        discipline_res = await session.execute(
            select(CompetitionDiscipline).where(
                CompetitionDiscipline.id == competition_discipline_id
            )
        )
        discipline = discipline_res.scalar_one_or_none()
        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        participant_res = await session.execute(
            select(Participant).where(
                Participant.competition_division_id == discipline.competition_division_id,
                Participant.athlete_id == payload.athlete_id,
            )
        )
        participant = participant_res.scalar_one_or_none()
        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found")

        existing_res = await session.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == competition_discipline_id,
                DisciplineResult.participant_id == participant.id,
            )
        )
        existing = existing_res.scalar_one_or_none()

        if existing:
            existing.primary_value = payload.primary_value
            existing.secondary_value = payload.secondary_value
            existing.status_flag = payload.status_flag
            obj = existing
        else:
            obj = DisciplineResult(
                competition_discipline_id=competition_discipline_id,
                participant_id=participant.id,
                primary_value=payload.primary_value,
                secondary_value=payload.secondary_value,
                status_flag=payload.status_flag,
            )
            session.add(obj)

        await session.commit()
        await session.refresh(obj)

        return DisciplineResultOut(
            id=obj.id,
            competition_discipline_id=obj.competition_discipline_id,
            participant_id=obj.participant_id,
            athlete_id=participant.athlete_id,
            primary_value=float(obj.primary_value) if obj.primary_value is not None else None,
            secondary_value=float(obj.secondary_value) if obj.secondary_value is not None else None,
            status_flag=obj.status_flag,
        )
