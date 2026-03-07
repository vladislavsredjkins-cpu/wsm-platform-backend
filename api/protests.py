from datetime import datetime
from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.database import SessionLocal
from models.athlete import Athlete
from models.competition import Competition
from models.protest import Protest


router = APIRouter(tags=["protests"])


ProtestStatus = Literal["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]


class ProtestCreate(BaseModel):
    competition_id: UUID
    athlete_id: UUID
    reason: str = Field(..., min_length=3, max_length=2000)


class ProtestReview(BaseModel):
    status: ProtestStatus


class ProtestOut(BaseModel):
    id: UUID
    competition_id: UUID
    athlete_id: UUID
    reason: str
    status: ProtestStatus
    created_at: datetime | None = None

    class Config:
        from_attributes = True


@router.post("/protests", response_model=ProtestOut)
async def create_protest(payload: ProtestCreate):
    async with SessionLocal() as session:
        competition = await session.get(Competition, payload.competition_id)
        if not competition:
            raise HTTPException(status_code=404, detail="Competition not found")

        athlete = await session.get(Athlete, payload.athlete_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")

        protest = Protest(
            competition_id=payload.competition_id,
            athlete_id=payload.athlete_id,
            reason=payload.reason,
            status="SUBMITTED",
        )

        session.add(protest)
        await session.commit()
        await session.refresh(protest)
        return protest


@router.get("/protests", response_model=list[ProtestOut])
async def list_protests(
    competition_id: UUID | None = None,
    athlete_id: UUID | None = None,
    status: ProtestStatus | None = None,
):
    async with SessionLocal() as session:
        stmt = select(Protest)

        if competition_id:
            stmt = stmt.where(Protest.competition_id == competition_id)

        if athlete_id:
            stmt = stmt.where(Protest.athlete_id == athlete_id)

        if status:
            stmt = stmt.where(Protest.status == status)

        stmt = stmt.order_by(Protest.created_at.desc())

        result = await session.execute(stmt)
        return list(result.scalars().all())


@router.get("/protests/{protest_id}", response_model=ProtestOut)
async def get_protest(protest_id: UUID):
    async with SessionLocal() as session:
        protest = await session.get(Protest, protest_id)
        if not protest:
            raise HTTPException(status_code=404, detail="Protest not found")
        return protest


@router.patch("/protests/{protest_id}/review", response_model=ProtestOut)
async def review_protest(protest_id: UUID, payload: ProtestReview):
    async with SessionLocal() as session:
        protest = await session.get(Protest, protest_id)
        if not protest:
            raise HTTPException(status_code=404, detail="Protest not found")

        protest.status = payload.status

        await session.commit()
        await session.refresh(protest)
        return protest
