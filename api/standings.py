from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from db.database import SessionLocal
from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from models.discipline_result import DisciplineResult
from models.participant import Participant
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
        discipline_res = await session.execute(
            select(CompetitionDiscipline).where(
                CompetitionDiscipline.id == competition_discipline_id
            )
        )
        discipline = discipline_res.scalar_one_or_none()
        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        result_res = await session.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == competition_discipline_id
            )
        )
        results = list(result_res.scalars().all())

        rows = []
        for result in results:
            participant = await session.get(Participant, result.participant_id)
            rows.append(
                {
                    "participant_id": result.participant_id,
                    "athlete_id": participant.athlete_id,
                    "bib_no": participant.bib_no,
                    "primary_value": float(result.primary_value) if result.primary_value is not None else None,
                    "secondary_value": float(result.secondary_value) if result.secondary_value is not None else None,
                    "status_flag": result.status_flag,
                }
            )

        mode = discipline.discipline_mode

        def sort_key(item: dict):
            status = item["status_flag"]
            status_rank = 0 if status == "OK" else 1

            primary_value = item["primary_value"]
            secondary_value = item["secondary_value"]

            pv_missing = primary_value is None
            sv_missing = secondary_value is None

            if mode == "TIME_WITH_DISTANCE_FALLBACK":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    primary_value if primary_value is not None else 10**12,
                    0 if not sv_missing else 1,
                    -(secondary_value if secondary_value is not None else -1),
                )

            if mode in ("AMRAP_REPS", "AMRAP_DISTANCE", "MAX_WEIGHT_WITHIN_CAP"):
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(primary_value if primary_value is not None else -1),
                )

            if mode == "RELAY_DUAL_METRIC":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(primary_value if primary_value is not None else -1),
                    0 if not sv_missing else 1,
                    secondary_value if secondary_value is not None else 10**12,
                )

            return (
                status_rank,
                0 if not pv_missing else 1,
                -(primary_value if primary_value is not None else -1),
            )

        rows_sorted = sorted(rows, key=sort_key)

        items_out: list[DisciplineLeaderboardRow] = []
        for idx, row in enumerate(rows_sorted, start=1):
            items_out.append(
                DisciplineLeaderboardRow(
                    participant_id=row["participant_id"],
                    athlete_id=row["athlete_id"],
                    bib_no=row["bib_no"],
                    place=idx,
                    primary_value=row["primary_value"],
                    secondary_value=row["secondary_value"],
                    status_flag=row["status_flag"],
                )
            )

        return DisciplineLeaderboardOut(
            competition_discipline_id=competition_discipline_id,
            discipline_mode=mode,
            items=items_out,
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
