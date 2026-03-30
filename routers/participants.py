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
# ── EVENTS PARTICIPANTS ───────────────────────────────────────────
from pydantic import BaseModel as PydanticBase
from typing import Optional
import datetime

class EventsParticipantCreate(PydanticBase):
    events_division_id: uuid.UUID
    competition_id: uuid.UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    country: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    bodyweight_kg: Optional[float] = None
    phone: Optional[str] = None

@router.post("/events")
async def create_events_participant(data: EventsParticipantCreate, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    result = await db.execute(text("""
        INSERT INTO events_participants 
        (events_division_id, competition_id, first_name, last_name, email, country, date_of_birth, bodyweight_kg, phone)
        VALUES (:div_id, :comp_id, :first_name, :last_name, :email, :country, :dob, :bw, :phone)
        RETURNING *
    """), {
        "div_id": str(data.events_division_id),
        "comp_id": str(data.competition_id),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "country": data.country,
        "dob": data.date_of_birth,
        "bw": data.bodyweight_kg,
        "phone": data.phone,
    })
    await db.commit()
    row = result.mappings().first()
    return dict(row)

@router.get("/events/competition/{competition_id}")
async def list_events_participants(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    result = await db.execute(text("""
        SELECT ep.*, ed.name as division_name 
        FROM events_participants ep
        LEFT JOIN events_divisions ed ON ep.events_division_id = ed.id
        WHERE ep.competition_id = :comp_id
        ORDER BY ed.name, ep.last_name
    """), {"comp_id": str(competition_id)})
    return [dict(r) for r in result.mappings().all()]

@router.get("/events/division/{events_division_id}")
async def list_events_participants_by_division(events_division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    result = await db.execute(text("""
        SELECT * FROM events_participants 
        WHERE events_division_id = :div_id
        ORDER BY bib_no, last_name
    """), {"div_id": str(events_division_id)})
    return [dict(r) for r in result.mappings().all()]

@router.patch("/events/{participant_id}/bib")
async def set_events_participant_bib(participant_id: uuid.UUID, bib_no: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    await db.execute(text(
        "UPDATE events_participants SET bib_no = :bib WHERE id = :id"
    ), {"bib": bib_no, "id": str(participant_id)})
    await db.commit()
    return {"status": "ok"}

@router.delete("/events/{participant_id}")
async def delete_events_participant(participant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    await db.execute(text(
        "DELETE FROM events_participants WHERE id = :id"
    ), {"id": str(participant_id)})
    await db.commit()
    return {"status": "ok"}
