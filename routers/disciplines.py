from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from services.discipline_standing_service import DisciplineStandingService
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


class DisciplineCreate(BaseModel):
    competition_division_id: uuid.UUID
    discipline_name: str
    discipline_mode: Optional[str] = None
    order_no: Optional[int] = 1
    time_cap_seconds: Optional[int] = None
    lanes_count: Optional[int] = None
    track_length_meters: Optional[Decimal] = None
    implement_weight: Optional[str] = None
    notes: Optional[str] = None


class DisciplineResponse(BaseModel):
    id: uuid.UUID
    competition_division_id: uuid.UUID
    discipline_name: str
    discipline_mode: Optional[str]
    order_no: Optional[int]
    time_cap_seconds: Optional[int]
    track_length_meters: Optional[Decimal]
    implement_weight: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DisciplineUpdate(BaseModel):
    discipline_name: Optional[str] = None
    discipline_mode: Optional[str] = None
    order_no: Optional[int] = None
    time_cap_seconds: Optional[int] = None
    track_length_meters: Optional[Decimal] = None
    implement_weight: Optional[str] = None
    notes: Optional[str] = None


@router.post("/", response_model=DisciplineResponse)
async def create_discipline(data: DisciplineCreate, db: AsyncSession = Depends(get_db)):
    division = await db.get(CompetitionDivision, data.competition_division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    discipline = CompetitionDiscipline(
        id=uuid.uuid4(),
        competition_division_id=data.competition_division_id,
        discipline_name=data.discipline_name,
        discipline_mode=data.discipline_mode,
        order_no=data.order_no,
        time_cap_seconds=data.time_cap_seconds,
        lanes_count=data.lanes_count,
        track_length_meters=data.track_length_meters,
        implement_weight=data.implement_weight,
        notes=data.notes,
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
        .order_by(CompetitionDiscipline.order_no)
    )
    return result.scalars().all()


@router.get("/{discipline_id}", response_model=DisciplineResponse)
async def get_discipline(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discipline


@router.patch("/{discipline_id}", response_model=DisciplineResponse)
async def update_discipline(discipline_id: uuid.UUID, data: DisciplineUpdate, db: AsyncSession = Depends(get_db)):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(discipline, field, value)
    await db.commit()
    await db.refresh(discipline)
    return discipline


@router.delete("/{discipline_id}")
async def delete_discipline(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    discipline = await db.get(CompetitionDiscipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    await db.delete(discipline)
    await db.commit()
    return {"status": "ok"}


@router.post("/{discipline_id}/calculate-standings")
async def calculate_standings(discipline_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = DisciplineStandingService(db)
    standings = await service.calculate(discipline_id)
    return {"status": "ok", "standings_created": len(standings)}

# ── EVENTS DISCIPLINES ────────────────────────────────────────────
@router.post("/events-division/{events_division_id}")
async def create_events_discipline(events_division_id: uuid.UUID, data: DisciplineCreate, db: AsyncSession = Depends(get_db)):
    from models.competition_discipline import CompetitionDiscipline
    discipline = CompetitionDiscipline(
        events_division_id=events_division_id,
        discipline_name=data.discipline_name,
        discipline_mode=data.discipline_mode,
        order_no=data.order_no,
        time_cap_seconds=data.time_cap_seconds,
        implement_weight=data.implement_weight,
        result_unit=data.result_unit,
        notes=data.notes,
    )
    db.add(discipline)
    await db.commit()
    await db.refresh(discipline)
    return discipline

@router.get("/events-division/{events_division_id}")
async def list_events_disciplines(events_division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from models.competition_discipline import CompetitionDiscipline
    result = await db.execute(
        select(CompetitionDiscipline)
        .where(CompetitionDiscipline.events_division_id == events_division_id)
        .order_by(CompetitionDiscipline.order_no)
    )
    return result.scalars().all()
