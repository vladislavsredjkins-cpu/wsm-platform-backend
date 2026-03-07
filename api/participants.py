from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.database import SessionLocal
from models.participant import Participant


router = APIRouter(tags=["participants"])


class ParticipantCreate(BaseModel):
    athlete_id: UUID
    bib_no: int | None = Field(None, ge=1, le=9999)
    bodyweight_kg: float | None = Field(None, ge=0.0, le=400.0)


class ParticipantOut(ParticipantCreate):
    id: UUID
    competition_division_id: UUID

    class Config:
        from_attributes = True


@router.post("/divisions/{division_id}/participants", response_model=ParticipantOut)
async def create_participant(division_id: UUID, payload: ParticipantCreate):
    async with SessionLocal() as session:
        participant = Participant(
            competition_division_id=division_id,
            athlete_id=payload.athlete_id,
            bib_no=payload.bib_no,
            bodyweight_kg=payload.bodyweight_kg,
        )
        session.add(participant)
        await session.commit()
        await session.refresh(participant)
        return participant


@router.get("/divisions/{division_id}/participants", response_model=list[ParticipantOut])
async def list_participants(division_id: UUID):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Participant).where(
                Participant.competition_division_id == division_id
            )
        )
        return list(result.scalars().all())
