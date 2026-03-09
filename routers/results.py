from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from auth.dependencies import require_referee
from models.user import User
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid
import datetime

router = APIRouter(prefix="/results", tags=["results"])


class ResultCreate(BaseModel):
    participant_id: uuid.UUID
    result_value: Optional[Decimal] = None
    is_zero: bool = False
    payload: Optional[dict] = None


class ResultResponse(BaseModel):
    id: uuid.UUID
    competition_discipline_id: uuid.UUID
    participant_id: uuid.UUID
    result_value: Optional[Decimal]
    is_zero: bool

    class Config:
        from_attributes = True


class StandingResponse(BaseModel):
    participant_id: uuid.UUID
    place: int
    points_for_discipline: Decimal

    class Config:
        from_attributes = True


@router.post("/discipline/{discipline_id}", response_model=ResultResponse)
async def upsert_result(
    discipline_id: uuid.UUID,
    data: ResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_referee),
):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")

    participant = await db.get(Participant, data.participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    if participant.competition_division_id != discipline.competition_division_id:
        raise HTTPException(status_code=400, detail="Participant does not belong to this discipline's division")

    result = await db.execute(
        select(DisciplineResult).where(
            DisciplineResult.competition_discipline_id == discipline_id,
            DisciplineResult.participant_id == data.participant_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.result_value = data.result_value
        existing.is_zero = data.is_zero
        existing.payload = data.payload
        obj = existing
    else:
        obj = DisciplineResult(
            id=uuid.uuid4(),
            competition_discipline_id=discipline_id,
            participant_id=data.participant_id,
            result_value=data.result_value,
            is_zero=data.is_zero,
            payload=data.payload,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(obj)

    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/discipline/{discipline_id}", response_model=list[ResultResponse])
async def list_results(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DisciplineResult)
        .where(DisciplineResult.competition_discipline_id == discipline_id)
    )
    return result.scalars().all()


@router.get("/discipline/{discipline_id}/standings", response_model=list[StandingResponse])
async def get_standings(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DisciplineStanding)
        .where(DisciplineStanding.competition_discipline_id == discipline_id)
        .order_by(DisciplineStanding.place)
    )
    return result.scalars().all()