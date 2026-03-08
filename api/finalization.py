from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.database import SessionLocal
from models.competition_division import CompetitionDivision, DivisionStatus
from services.competition_engine import CompetitionEngine
from services.ranking_engine import RankingEngine


router = APIRouter(tags=["finalization"])


class OverallStandingRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    total_points: float
    place: int
    tie_break_value: float | None = None


class OverallStandingOut(BaseModel):
    division_id: UUID
    items: list[OverallStandingRow]


@router.post("/divisions/{division_id}/calculate-standings", response_model=OverallStandingOut)
async def calculate_standings(division_id: UUID):
    async with SessionLocal() as session:
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status in (DivisionStatus.RESULTS_VALIDATED, DivisionStatus.LOCKED):
            raise HTTPException(
                status_code=400,
                detail="Standings are already validated or locked",
            )

        engine = CompetitionEngine(session)

        try:
            items_data = await engine.calculate_and_store_division_standings(division_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        items = [OverallStandingRow(**item) for item in items_data]

        return OverallStandingOut(
            division_id=division_id,
            items=items,
        )


@router.post("/divisions/{division_id}/results/validate", response_model=OverallStandingOut)
async def validate_division_results(division_id: UUID):
    async with SessionLocal() as session:
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status in (DivisionStatus.RESULTS_VALIDATED, DivisionStatus.LOCKED):
            raise HTTPException(
                status_code=400,
                detail="Standings are already validated or locked",
            )

        engine = CompetitionEngine(session)

        try:
            items_data = await engine.calculate_and_store_division_standings(division_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        div.status = DivisionStatus.RESULTS_VALIDATED
        await session.commit()

        items = [OverallStandingRow(**item) for item in items_data]

        return OverallStandingOut(
            division_id=division_id,
            items=items,
        )


@router.post("/divisions/{division_id}/lock")
async def lock_division(division_id: UUID):
    async with SessionLocal() as session:
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status != DivisionStatus.RESULTS_VALIDATED:
            raise HTTPException(
                status_code=400,
                detail="Division must be RESULTS_VALIDATED before lock",
            )

        if div.q_effective is None:
            raise HTTPException(
                status_code=400,
                detail="Division q_effective must be set before lock",
            )

        div.status = DivisionStatus.LOCKED
        div.locked_at = datetime.utcnow()

        await session.commit()

    try:
        engine = RankingEngine()
        await engine.process_division(division_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Division locked, but ranking update failed: {str(exc)}",
        ) from exc

    return {
        "division_id": division_id,
        "status": DivisionStatus.LOCKED.value,
    }
