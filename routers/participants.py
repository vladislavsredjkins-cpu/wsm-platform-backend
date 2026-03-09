from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.participant import Participant
from models.competition_division import CompetitionDivision
from models.athlete import Athlete
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid
import datetime

router = APIRouter(prefix="/participants", tags=["participants"])


class ParticipantCreate(BaseModel):
    competition_division_id: uuid.UUID
    athlete_id: uuid.UUID
    weight_in: Optional[Decimal] = None


class ParticipantResponse(BaseModel):
    id: uuid.UUID
    competition_division_id: uuid.UUID
    athlete_id: uuid.UUID
    weight_in: Optional[Decimal]
    status: str

    class Config:
        from_attributes = True


@router.post("/", response_model=ParticipantResponse)
async def create_participant(data: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    division = await db.get(CompetitionDivision, data.competition_division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")

    if division.is_locked:
        raise HTTPException(status_code=400, detail="Division is locked — cannot add participants")

    athlete = await db.get(Athlete, data.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # проверяем что атлет не зарегистрирован дважды
    result = await db.execute(
        select(Participant).where(
            Participant.competition_division_id == data.competition_division_id,
            Participant.athlete_id == data.athlete_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Athlete already registered in this division")

    participant = Participant(
        id=uuid.uuid4(),
        competition_division_id=data.competition_division_id,
        athlete_id=data.athlete_id,
        weight_in=data.weight_in,
        status="REGISTERED",
        created_at=datetime.datetime.utcnow(),
    )
    
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant


@router.get("/division/{division_id}", response_model=list[ParticipantResponse])
async def list_participants(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Participant)
        .where(Participant.competition_division_id == division_id)
        .order_by(Participant.created_at)
    )
    return result.scalars().all()


@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(participant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    participant = await db.get(Participant, participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant