from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db.database import SessionLocal
from services.competition_engine import CompetitionEngine


router = APIRouter(tags=["standings"])


DisciplineMode = Literal[
    "TIME_WITH_DISTANCE_FALLBACK",
    "AMRAP_REPS",
    "AMRAP_DISTANCE",
    "MAX_WEIGHT_WITHIN_CAP",
    "RELAY_DUAL_METRIC",
]

StatusFlag = Literal["OK", "DNF", "DQ", "DNS"]


class DisciplineLeaderboardRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    place: int
    primary_value: float | None = None
    secondary_value: float | None = None
    status_flag: StatusFlag


class DisciplineLeaderboardOut(BaseModel):
    competition_discipline_id: UUID
    discipline_mode: DisciplineMode
    items: list[DisciplineLeaderboardRow]


class DivisionOverallRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    total_points: float
    place: int


class DivisionOverallOut(BaseModel):
    division_id: UUID
    items: list[DivisionOverallRow]


@router.get(
    "/disciplines/{competition_discipline_id}/leaderboard",
    response_model=DisciplineLeaderboardOut,
)
async def discipline_leaderboard(competition_discipline_id: UUID):
    async with SessionLocal() as session:
        engine = CompetitionEngine(session)

        try:
            data = await engine.calculate_discipline_leaderboard(
                competition_discipline_id
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        items = [DisciplineLeaderboardRow(**item) for item in data["items"]]

        return DisciplineLeaderboardOut(
            competition_discipline_id=data["competition_discipline_id"],
            discipline_mode=data["discipline_mode"],
            items=items,
        )

@router.get("/divisions/{division_id}/leaderboard", response_model=DivisionOverallOut)
async def division_leaderboard(division_id: UUID):
    async with SessionLocal() as session:
        engine = CompetitionEngine(session)

        try:
            items_data = await engine.calculate_division_standings(division_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        items = [DivisionOverallRow(**item) for item in items_data]

        return DivisionOverallOut(
            division_id=division_id,
            items=items,
        )
