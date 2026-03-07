from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
import sqlalchemy as sa

from db.database import SessionLocal
from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.participant import Participant


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

        if div.status in ("RESULTS_VALIDATED", "LOCKED"):
            raise HTTPException(
                status_code=400,
                detail="Standings are already validated or locked",
            )

        p_res = await session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(p_res.scalars().all())
        if not participants:
            return OverallStandingOut(division_id=division_id, items=[])

        participant_ids = [p.id for p in participants]
        p_map = {p.id: p for p in participants}

        d_res = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(d_res.scalars().all())

        await session.execute(
            sa.delete(DisciplineStanding).where(
                DisciplineStanding.competition_discipline_id.in_(
                    select(CompetitionDiscipline.id).where(
                        CompetitionDiscipline.competition_division_id == division_id
                    )
                )
            )
        )

        await session.execute(
            sa.delete(OverallStanding).where(
                OverallStanding.competition_division_id == division_id
            )
        )

        points_map: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}

        def sort_key_for_mode(mode: str, item: dict):
            status = item["status_flag"]
            status_rank = 0 if status == "OK" else 1

            pv = item["primary_value"]
            sv = item["secondary_value"]

            pv_missing = pv is None
            sv_missing = sv is None

            if mode == "TIME_WITH_DISTANCE_FALLBACK":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    pv if pv is not None else 10**12,
                    0 if not sv_missing else 1,
                    -(sv if sv is not None else -1),
                )

            if mode in ("AMRAP_REPS", "AMRAP_DISTANCE", "MAX_WEIGHT_WITHIN_CAP"):
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                )

            if mode == "RELAY_DUAL_METRIC":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                    0 if not sv_missing else 1,
                    sv if sv is not None else 10**12,
                )

            return (
                status_rank,
                0 if not pv_missing else 1,
                -(pv if pv is not None else -1),
            )

        for disc in disciplines:
            r_res = await session.execute(
                select(DisciplineResult).where(
                    DisciplineResult.competition_discipline_id == disc.id,
                    DisciplineResult.participant_id.in_(participant_ids),
                )
            )
            results = list(r_res.scalars().all())
            results_by_pid = {r.participant_id: r for r in results}

            rows = []
            for pid in participant_ids:
                r = results_by_pid.get(pid)
                if r:
                    rows.append(
                        {
                            "participant_id": pid,
                            "status_flag": r.status_flag,
                            "primary_value": float(r.primary_value) if r.primary_value is not None else None,
                            "secondary_value": float(r.secondary_value) if r.secondary_value is not None else None,
                        }
                    )
                else:
                    rows.append(
                        {
                            "participant_id": pid,
                            "status_flag": "DNS",
                            "primary_value": None,
                            "secondary_value": None,
                        }
                    )

            rows_sorted = sorted(rows, key=lambda x: sort_key_for_mode(disc.discipline_mode, x))

            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                pid = row["participant_id"]
                pts = float(n - idx + 1)
                points_map[pid] += pts

                session.add(
                    DisciplineStanding(
                        competition_discipline_id=disc.id,
                        participant_id=pid,
                        place=idx,
                        points_for_discipline=pts,
                    )
                )

        overall_rows = []
        for pid in participant_ids:
            tie_break_value = None
            overall_rows.append(
                {
                    "participant_id": pid,
                    "total_points": float(points_map[pid]),
                    "tie_break_value": tie_break_value,
                }
            )

        overall_rows_sorted = sorted(
            overall_rows,
            key=lambda x: (
                -x["total_points"],
                str(x["participant_id"]),
            ),
        )

        items_out = []
        for place_no, row in enumerate(overall_rows_sorted, start=1):
            pid = row["participant_id"]
            p = p_map[pid]

            session.add(
                OverallStanding(
                    competition_division_id=division_id,
                    participant_id=pid,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

            items_out.append(
                OverallStandingRow(
                    participant_id=pid,
                    athlete_id=p.athlete_id,
                    bib_no=p.bib_no,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

        await session.commit()

        return OverallStandingOut(
            division_id=division_id,
            items=items_out,
        )


@router.post("/divisions/{division_id}/results/validate", response_model=OverallStandingOut)
async def validate_division_results(division_id: UUID):
    async with SessionLocal() as session:
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        standings = await calculate_standings(division_id)

        div.status = "RESULTS_VALIDATED"

        await session.commit()

        return standings


@router.post("/divisions/{division_id}/lock")
async def lock_division(division_id: UUID):
    async with SessionLocal() as session:
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status != "RESULTS_VALIDATED":
            raise HTTPException(
                status_code=400,
                detail="Division must be RESULTS_VALIDATED before lock",
            )

        div.status = "LOCKED"
        div.locked_at = datetime.utcnow()

        await session.commit()

        return {
            "division_id": division_id,
            "status": "LOCKED",
        }
