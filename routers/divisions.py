from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition_division import CompetitionDivision
from models.competition_division_q import CompetitionDivisionQ
from services.finalization_service import FinalizationService
from services.overall_standing_service import OverallStandingService
from services.ranking_service import RankingService
from auth.dependencies import require_admin, require_federation, require_referee
from models.user import User
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import uuid
import datetime

router = APIRouter(prefix="/divisions", tags=["divisions"])


class DivisionCreate(BaseModel):
    competition_id: uuid.UUID
    division_key: str
    format: str


class DivisionQCreate(BaseModel):
    q_base: Decimal
    q_effective: Decimal
    policy_version: str = "1.0"


class DivisionResponse(BaseModel):
    id: uuid.UUID
    competition_id: uuid.UUID
    division_key: str
    format: str
    status: str
    locked_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=DivisionResponse)
async def create_division(data: DivisionCreate, db: AsyncSession = Depends(get_db)):
    division = CompetitionDivision(
        id=uuid.uuid4(),
        competition_id=data.competition_id,
        division_key=data.division_key,
        format=data.format,
        status="DRAFT",
        
        
    )
    db.add(division)
    await db.commit()
    await db.refresh(division)
    return division


@router.get("/{division_id}", response_model=DivisionResponse)
async def get_division(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CompetitionDivision).where(CompetitionDivision.id == division_id))
    division = result.scalar_one_or_none()
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    return division


@router.post("/{division_id}/q")
async def set_division_q(division_id: uuid.UUID, data: DivisionQCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CompetitionDivisionQ).where(CompetitionDivisionQ.competition_division_id == division_id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.q_base = data.q_base
        existing.q_effective = data.q_effective
        existing.policy_version = data.policy_version
        existing.confirmed_at = datetime.datetime.utcnow()
    else:
        q = CompetitionDivisionQ(
            id=uuid.uuid4(),
            competition_division_id=division_id,
            q_base=data.q_base,
            q_effective=data.q_effective,
            policy_version=data.policy_version,
            confirmed_at=datetime.datetime.utcnow(),
        )
        db.add(q)

    await db.commit()
    return {"status": "ok", "division_id": str(division_id), "q_effective": str(data.q_effective)}


@router.post("/{division_id}/validate")
async def validate_division(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = FinalizationService(db)
    result = await service.validate(division_id)
    return result


@router.post("/{division_id}/lock")
async def lock_division(
    division_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_federation),
):
    service = FinalizationService(db)
    try:
        division = await service.lock(division_id)
        return {"status": "locked", "division_id": str(division.id), "locked_at": division.locked_at}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{division_id}/process-ranking")
async def process_ranking(
    division_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    service = RankingService(db)
    try:
        awards = await service.process_division(division_id)
        return {"status": "ok", "awards_created": len(awards)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{division_id}/calculate-overall")
async def calculate_overall(
    division_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_referee),
):
    service = OverallStandingService(db)
    standings = await service.calculate(division_id)
    return {"status": "ok", "standings_created": len(standings)}

@router.get("/competition/{competition_id}", response_model=list[DivisionResponse])
async def list_divisions(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CompetitionDivision)
        .where(CompetitionDivision.competition_id == competition_id)
        .order_by(CompetitionDivision.division_key)
    )
    return result.scalars().all()

@router.delete("/{division_id}")
async def delete_division(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.participant import Participant
    # Check participants
    parts = await db.execute(select(Participant).where(Participant.competition_division_id == division_id))
    if parts.scalars().first():
        raise HTTPException(400, "Cannot delete division with registered athletes")
    # Check status
    div = await db.get(CompetitionDivision, division_id)
    if not div:
        raise HTTPException(404, "Division not found")
    if div.status not in ('DRAFT', 'SUBMITTED'):
        raise HTTPException(400, f"Cannot delete division with status {div.status}")
    from sqlalchemy import text
    # Delete via raw SQL to handle all FK constraints
    await db.execute(text("DELETE FROM competition_divisions WHERE id = :id"), {"id": division_id})
    await db.commit()
    return {"status": "deleted"}
