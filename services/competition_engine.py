from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from models.discipline_result import DisciplineResult
from models.participant import Participant
from services.discipline_engine import DisciplineEngine

import sqlalchemy as sa
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding


class CompetitionEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.discipline_engine = DisciplineEngine()

    
        async def calculate_and_store_division_standings(self, division_id: UUID):
        division_res = await self.session.execute(
            select(CompetitionDivision).where(CompetitionDivision.id == division_id)
        )
        division = division_res.scalar_one_or_none()
        if not division:
            raise ValueError("Division not found")

        participant_res = await self.session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(participant_res.scalars().all())
        participant_ids = [p.id for p in participants]
        p_map = {p.id: p for p in participants}

        if not participant_ids:
            return []

        discipline_res = await self.session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(discipline_res.scalars().all())

        await self.session.execute(
            sa.delete(DisciplineStanding).where(
                DisciplineStanding.competition_discipline_id.in_(
                    select(CompetitionDiscipline.id).where(
                        CompetitionDiscipline.competition_division_id == division_id
                    )
                )
            )
        )

        await self.session.execute(
            sa.delete(OverallStanding).where(
                OverallStanding.competition_division_id == division_id
            )
        )

        points_map: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}
        place_counts_map: dict[UUID, dict[int, int]] = {
            pid: {} for pid in participant_ids
        }

        for disc in disciplines:
            r_res = await self.session.execute(
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

            rows_sorted = sorted(
                rows,
                key=lambda x: self.discipline_engine.sort_key_for_mode(
                    disc.discipline_mode, x
                ),
            )

            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                pid = row["participant_id"]
                pts = float(n - idx + 1)
                points_map[pid] += pts

                place_counts_map[pid][idx] = place_counts_map[pid].get(idx, 0) + 1

                self.session.add(
                    DisciplineStanding(
                        competition_discipline_id=disc.id,
                        participant_id=pid,
                        place=idx,
                        points_for_discipline=pts,
                    )
                )

        max_place = len(participant_ids)

        def tie_vector(pid: UUID) -> tuple[int, ...]:
            counts = place_counts_map.get(pid, {})
            return tuple(counts.get(place_no, 0) for place_no in range(1, max_place + 1))

        def bodyweight_value(pid: UUID) -> float:
            bw = p_map[pid].bodyweight_kg
            return float(bw) if bw is not None else 10**12

        overall_rows = []
        for pid in participant_ids:
            overall_rows.append(
                {
                    "participant_id": pid,
                    "total_points": float(points_map[pid]),
                    "tie_vector": tie_vector(pid),
                    "tie_break_value": float(p_map[pid].bodyweight_kg) if p_map[pid].bodyweight_kg is not None else None,
                }
            )

        overall_rows_sorted = sorted(
            overall_rows,
            key=lambda x: (
                -x["total_points"],
                *[-v for v in x["tie_vector"]],
                bodyweight_value(x["participant_id"]),
                str(x["participant_id"]),
            ),
        )

        def same_rank_key(a: dict, b: dict) -> bool:
            return (
                a["total_points"] == b["total_points"]
                and a["tie_vector"] == b["tie_vector"]
                and a["tie_break_value"] == b["tie_break_value"]
            )

        items = []
        current_place = 1

        for idx, row in enumerate(overall_rows_sorted):
            if idx == 0:
                place_no = 1
            else:
                prev = overall_rows_sorted[idx - 1]
                if same_rank_key(prev, row):
                    place_no = current_place
                else:
                    place_no = idx + 1
                    current_place = place_no

            pid = row["participant_id"]
            p = p_map[pid]

            self.session.add(
                OverallStanding(
                    competition_division_id=division_id,
                    participant_id=pid,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

            items.append(
                {
                    "participant_id": pid,
                    "athlete_id": p.athlete_id,
                    "bib_no": p.bib_no,
                    "total_points": row["total_points"],
                    "place": place_no,
                    "tie_break_value": row["tie_break_value"],
                }
            )

        await self.session.commit()

        return items
        
    async def calculate_discipline_leaderboard(self, competition_discipline_id: UUID):
        discipline_res = await self.session.execute(
            select(CompetitionDiscipline).where(
                CompetitionDiscipline.id == competition_discipline_id
            )
        )
        discipline = discipline_res.scalar_one_or_none()
        if not discipline:
            raise ValueError("Discipline not found")

        result_res = await self.session.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == competition_discipline_id
            )
        )
        results = list(result_res.scalars().all())

        rows = []
        for result in results:
            participant = await self.session.get(Participant, result.participant_id)
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
        rows_sorted = sorted(
            rows,
            key=lambda x: self.discipline_engine.sort_key_for_mode(mode, x),
        )

        items = []
        for idx, row in enumerate(rows_sorted, start=1):
            items.append(
                {
                    "participant_id": row["participant_id"],
                    "athlete_id": row["athlete_id"],
                    "bib_no": row["bib_no"],
                    "place": idx,
                    "primary_value": row["primary_value"],
                    "secondary_value": row["secondary_value"],
                    "status_flag": row["status_flag"],
                }
            )

        return {
            "competition_discipline_id": competition_discipline_id,
            "discipline_mode": mode,
            "items": items,
        }
        
    async def calculate_and_store_division_standings(self, division_id: UUID):
        division_res = await self.session.execute(
            select(CompetitionDivision).where(CompetitionDivision.id == division_id)
        )
        division = division_res.scalar_one_or_none()
        if not division:
            raise ValueError("Division not found")
    
        participant_res = await self.session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(participant_res.scalars().all())
        participant_ids = [p.id for p in participants]
        p_map = {p.id: p for p in participants}
    
        if not participant_ids:
            return []
    
        discipline_res = await self.session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(discipline_res.scalars().all())
    
        await self.session.execute(
            sa.delete(DisciplineStanding).where(
                DisciplineStanding.competition_discipline_id.in_(
                    select(CompetitionDiscipline.id).where(
                        CompetitionDiscipline.competition_division_id == division_id
                    )
                )
            )
        )
    
        await self.session.execute(
            sa.delete(OverallStanding).where(
                OverallStanding.competition_division_id == division_id
            )
        )
    
        points_map: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}
    
        for disc in disciplines:
            r_res = await self.session.execute(
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
    
            rows_sorted = sorted(
                rows,
                key=lambda x: self.discipline_engine.sort_key_for_mode(
                    disc.discipline_mode, x
                ),
            )
    
            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                pid = row["participant_id"]
                pts = float(n - idx + 1)
                points_map[pid] += pts
    
                self.session.add(
                    DisciplineStanding(
                        competition_discipline_id=disc.id,
                        participant_id=pid,
                        place=idx,
                        points_for_discipline=pts,
                    )
                )
    
        overall_rows = []
        for pid in participant_ids:
            overall_rows.append(
                {
                    "participant_id": pid,
                    "total_points": float(points_map[pid]),
                    "tie_break_value": None,
                }
            )
    
        overall_rows_sorted = sorted(
            overall_rows,
            key=lambda x: (-x["total_points"], str(x["participant_id"])),
        )
    
        items = []
        for place_no, row in enumerate(overall_rows_sorted, start=1):
            pid = row["participant_id"]
            p = p_map[pid]
    
            self.session.add(
                OverallStanding(
                    competition_division_id=division_id,
                    participant_id=pid,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )
    
            items.append(
                {
                    "participant_id": pid,
                    "athlete_id": p.athlete_id,
                    "bib_no": p.bib_no,
                    "total_points": row["total_points"],
                    "place": place_no,
                    "tie_break_value": row["tie_break_value"],
                }
            )
    
        await self.session.commit()
    
        return items
