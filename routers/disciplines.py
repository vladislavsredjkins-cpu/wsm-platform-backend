from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from services.discipline_standing_service import DisciplineStandingService
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


class DisciplineCreate(BaseModel):
    competition_division_id: uuid.UUID
    name: str
    discipline_mode: str
    sort_order: int = 1


class DisciplineResponse(BaseModel):
    id: uuid.UUID
    competition_division_id: uuid.UUID
    name: str
    discipline_mode: str
    sort_order: int

    class Config:
        from_attributes = True


@router.post("/", response_model=DisciplineResponse, tags=["disciplines"])
async def create_discipline(data: DisciplineCreate, db: AsyncSession = Depends(get_db)):
    division = await db.get(CompetitionDivision, data.competition_division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")

    discipline = CompetitionDiscipline(
        id=uuid.uuid4(),
        competition_division_id=data.competition_division_id,
        name=data.name,
        discipline_mode=data.discipline_mode,
        sort_order=data.sort_order,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(discipline)
    await db.commit()
    await db.refresh(discipline)
    return discipline


@router.get("/division/{division_id}", response_model=list[DisciplineResponse])
async def list_disciplines(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CompetitionDiscipline)
        .where(CompetitionDiscipline.competition_division_id == division_id)
        .order_by(CompetitionDiscipline.sort_order)
    )
    return result.scalars().all()


@router.get("/{discipline_id}", response_model=DisciplineResponse)
async def get_discipline(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discipline


@router.post("/{discipline_id}/calculate-standings")
async def calculate_standings(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = DisciplineStandingService(db)
    standings = await service.calculate(discipline_id)
    return {"status": "ok", "standings_created": len(standings)}