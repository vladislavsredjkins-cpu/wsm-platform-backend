from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.database import get_db
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.athlete import Athlete
from auth.dependencies import require_referee
from models.user import User
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid

router = APIRouter(prefix="/results", tags=["results"])


class ResultUpsert(BaseModel):
    participant_id: uuid.UUID
    primary_value: Optional[Decimal] = None
    secondary_value: Optional[Decimal] = None
    status_flag: Optional[str] = None


class ResultResponse(BaseModel):
    id: uuid.UUID
    competition_discipline_id: uuid.UUID
    participant_id: uuid.UUID
    primary_value: Optional[Decimal]
    secondary_value: Optional[Decimal]
    status_flag: Optional[str]

    class Config:
        from_attributes = True


class ParticipantWithResult(BaseModel):
    participant_id: uuid.UUID
    bib_no: Optional[int]
    first_name: str
    last_name: str
    country: Optional[str]
    primary_value: Optional[Decimal] = None
    secondary_value: Optional[Decimal] = None
    status_flag: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/discipline/{discipline_id}/sheet", response_model=list[ParticipantWithResult])
async def get_result_sheet(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")

    participants = await db.execute(
        select(Participant)
        .where(Participant.competition_division_id == discipline.competition_division_id)
        .options(selectinload(Participant.athlete))
        .order_by(Participant.bib_no)
    )
    participants = participants.scalars().all()

    results = await db.execute(
        select(DisciplineResult)
        .where(DisciplineResult.competition_discipline_id == discipline_id)
    )
    results_map = {r.participant_id: r for r in results.scalars().all()}

    sheet = []
    for p in participants:
        r = results_map.get(p.id)
        sheet.append(ParticipantWithResult(
            participant_id=p.id,
            bib_no=p.bib_no,
            first_name=p.athlete.first_name,
            last_name=p.athlete.last_name,
            country=p.athlete.country,
            primary_value=r.primary_value if r else None,
            secondary_value=r.secondary_value if r else None,
            status_flag=r.status_flag if r else None,
        ))
    return sheet


@router.post("/discipline/{discipline_id}", response_model=ResultResponse)
async def upsert_result(
    discipline_id: uuid.UUID,
    data: ResultUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_referee),
):
    existing = await db.execute(
        select(DisciplineResult).where(
            DisciplineResult.competition_discipline_id == discipline_id,
            DisciplineResult.participant_id == data.participant_id,
        )
    )
    existing = existing.scalar_one_or_none()

    if existing:
        existing.primary_value = data.primary_value
        existing.secondary_value = data.secondary_value
        existing.status_flag = data.status_flag
        obj = existing
    else:
        obj = DisciplineResult(
            id=uuid.uuid4(),
            competition_discipline_id=discipline_id,
            participant_id=data.participant_id,
            primary_value=data.primary_value,
            secondary_value=data.secondary_value,
            status_flag=data.status_flag,
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
