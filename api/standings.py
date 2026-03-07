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
        division_res = await session.execute(
            select(CompetitionDivision).where(CompetitionDivision.id == division_id)
        )
        division = division_res.scalar_one_or_none()
        if not division:
            raise HTTPException(status_code=404, detail="Division not found")

        participant_res = await session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(participant_res.scalars().all())
        participant_ids = [participant.id for participant in participants]

        if not participant_ids:
            return DivisionOverallOut(division_id=division_id, items=[])

        participant_map = {participant.id: participant for participant in participants}

        discipline_res = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(discipline_res.scalars().all())

        points: dict[UUID, float] = {participant_id: 0.0 for participant_id in participant_ids}

        def sort_key_for_mode(mode: str, item: dict):
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

        for discipline in disciplines:
            result_res = await session.execute(
                select(DisciplineResult).where(
                    DisciplineResult.competition_discipline_id == discipline.id,
                    DisciplineResult.participant_id.in_(participant_ids),
                )
            )
            results = list(result_res.scalars().all())
            results_by_pid = {result.participant_id: result for result in results}

            rows = []
            for participant_id in participant_ids:
                result = results_by_pid.get(participant_id)
                if result:
                    rows.append(
                        {
                            "participant_id": participant_id,
                            "status_flag": result.status_flag,
                            "primary_value": float(result.primary_value) if result.primary_value is not None else None,
                            "secondary_value": float(result.secondary_value) if result.secondary_value is not None else None,
                        }
                    )
                else:
                    rows.append(
                        {
                            "participant_id": participant_id,
                            "status_flag": "DNS",
                            "primary_value": None,
                            "secondary_value": None,
                        }
                    )

            rows_sorted = sorted(rows, key=lambda x: sort_key_for_mode(discipline.discipline_mode, x))

            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                participant_id = row["participant_id"]
                pts = float(n - idx + 1)
                points[participant_id] += pts

        overall = sorted(points.items(), key=lambda kv: (-kv[1], str(kv[0])))

        items: list[DivisionOverallRow] = []
        for place_no, (participant_id, total) in enumerate(overall, start=1):
            participant = participant_map[participant_id]
            items.append(
                DivisionOverallRow(
                    participant_id=participant_id,
                    athlete_id=participant.athlete_id,
                    bib_no=participant.bib_no,
                    total_points=total,
                    place=place_no,
                )
            )

        return DivisionOverallOut(division_id=division_id, items=items)
