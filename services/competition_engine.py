from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.competition_discipline import CompetitionDiscipline
from models.competition_division import CompetitionDivision
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.participant import Participant
from services.discipline_engine import DisciplineEngine


class CompetitionEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.discipline_engine = DisciplineEngine()

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
            if participant is None:
                continue

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

        def same_sport_result(a: dict, b: dict) -> bool:
            return self.discipline_engine.sort_key_for_mode(
                discipline.discipline_mode, a
            ) == self.discipline_engine.sort_key_for_mode(
                discipline.discipline_mode, b
            )

        rows_sorted = sorted(
            rows,
            key=lambda x: self.discipline_engine.sort_key_for_mode(
                discipline.discipline_mode, x
            ),
        )

        items = []
        idx = 0
        n = len(rows_sorted)

        while idx < n:
            row = rows_sorted[idx]
            group_end = idx + 1

            while group_end < n and same_sport_result(row, rows_sorted[group_end]):
                group_end += 1

            tie_group = rows_sorted[idx:group_end]
            place_no = idx + 1

            for tied_row in tie_group:
                items.append(
                    {
                        "participant_id": tied_row["participant_id"],
                        "athlete_id": tied_row["athlete_id"],
                        "bib_no": tied_row["bib_no"],
                        "place": place_no,
                        "primary_value": tied_row["primary_value"],
                        "secondary_value": tied_row["secondary_value"],
                        "status_flag": tied_row["status_flag"],
                    }
                )

            idx = group_end

        return {
            "competition_discipline_id": competition_discipline_id,
            "discipline_mode": discipline.discipline_mode,
            "items": items,
        }

    async def calculate_division_standings(self, division_id: UUID):
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
        participant_ids = [participant.id for participant in participants]
        participant_map = {participant.id: participant for participant in participants}

        if not participant_ids:
            return []

        discipline_res = await self.session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(discipline_res.scalars().all())

        points_map: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}
        place_counts_map: dict[UUID, dict[int, int]] = {
            pid: {} for pid in participant_ids
        }

        def status_points_eligible(status_flag: str) -> bool:
            return status_flag not in ("DNS", "DQ", "DNF")

        def same_sport_result(a: dict, b: dict, mode: str) -> bool:
            return self.discipline_engine.sort_key_for_mode(
                mode, a
            ) == self.discipline_engine.sort_key_for_mode(
                mode, b
            )

        def place_points(place_no: int, total_n: int) -> float:
            return float(total_n - place_no + 1)

        for discipline in disciplines:
            result_res = await self.session.execute(
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

            rows_sorted = sorted(
                rows,
                key=lambda x: self.discipline_engine.sort_key_for_mode(
                    discipline.discipline_mode, x
                ),
            )

            total_n = len(rows_sorted)
            idx = 0

            while idx < total_n:
                row = rows_sorted[idx]
                group_end = idx + 1

                while group_end < total_n and same_sport_result(
                    row, rows_sorted[group_end], discipline.discipline_mode
                ):
                    group_end += 1

                occupied_places = list(range(idx + 1, group_end + 1))
                tie_group = rows_sorted[idx:group_end]

                eligible_rows = [
                    tie_row
                    for tie_row in tie_group
                    if status_points_eligible(tie_row["status_flag"])
                ]

                if eligible_rows:
                    avg_points = sum(
                        place_points(place_no, total_n) for place_no in occupied_places
                    ) / len(occupied_places)
                else:
                    avg_points = 0.0

                for tie_row in tie_group:
                    participant_id = tie_row["participant_id"]
                    place_no = idx + 1

                    if status_points_eligible(tie_row["status_flag"]):
                        pts = float(avg_points)
                    else:
                        pts = 0.0

                    points_map[participant_id] += pts
                    place_counts_map[participant_id][place_no] = (
                        place_counts_map[participant_id].get(place_no, 0) + 1
                    )

                idx = group_end

        max_place = len(participant_ids)

        def tie_vector(participant_id: UUID) -> tuple[int, ...]:
            counts = place_counts_map.get(participant_id, {})
            return tuple(
                counts.get(place_no, 0) for place_no in range(1, max_place + 1)
            )

        def bodyweight_value(participant_id: UUID) -> float:
            bw = participant_map[participant_id].bodyweight_kg
            return float(bw) if bw is not None else 10**12

        overall_rows = []
        for participant_id in participant_ids:
            participant = participant_map[participant_id]
            overall_rows.append(
                {
                    "participant_id": participant_id,
                    "athlete_id": participant.athlete_id,
                    "bib_no": participant.bib_no,
                    "total_points": float(points_map[participant_id]),
                    "tie_vector": tie_vector(participant_id),
                    "tie_break_value": float(participant.bodyweight_kg)
                    if participant.bodyweight_kg is not None
                    else None,
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

            items.append(
                {
                    "participant_id": row["participant_id"],
                    "athlete_id": row["athlete_id"],
                    "bib_no": row["bib_no"],
                    "total_points": row["total_points"],
                    "place": place_no,
                    "tie_break_value": row["tie_break_value"],
                }
            )

        return items

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
        participant_ids = [participant.id for participant in participants]
        participant_map = {participant.id: participant for participant in participants}

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

        def status_points_eligible(status_flag: str) -> bool:
            return status_flag not in ("DNS", "DQ", "DNF")

        def same_sport_result(a: dict, b: dict, mode: str) -> bool:
            return self.discipline_engine.sort_key_for_mode(
                mode, a
            ) == self.discipline_engine.sort_key_for_mode(
                mode, b
            )

        def place_points(place_no: int, total_n: int) -> float:
            return float(total_n - place_no + 1)

        for discipline in disciplines:
            result_res = await self.session.execute(
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

            rows_sorted = sorted(
                rows,
                key=lambda x: self.discipline_engine.sort_key_for_mode(
                    discipline.discipline_mode, x
                ),
            )

            total_n = len(rows_sorted)
            idx = 0

            while idx < total_n:
                row = rows_sorted[idx]
                group_end = idx + 1

                while group_end < total_n and same_sport_result(
                    row, rows_sorted[group_end], discipline.discipline_mode
                ):
                    group_end += 1

                occupied_places = list(range(idx + 1, group_end + 1))
                tie_group = rows_sorted[idx:group_end]

                eligible_rows = [
                    tie_row
                    for tie_row in tie_group
                    if status_points_eligible(tie_row["status_flag"])
                ]

                if eligible_rows:
                    avg_points = sum(
                        place_points(place_no, total_n) for place_no in occupied_places
                    ) / len(occupied_places)
                else:
                    avg_points = 0.0

                for tie_row in tie_group:
                    participant_id = tie_row["participant_id"]
                    place_no = idx + 1

                    if status_points_eligible(tie_row["status_flag"]):
                        pts = float(avg_points)
                    else:
                        pts = 0.0

                    points_map[participant_id] += pts
                    place_counts_map[participant_id][place_no] = (
                        place_counts_map[participant_id].get(place_no, 0) + 1
                    )

                    self.session.add(
                        DisciplineStanding(
                            competition_discipline_id=discipline.id,
                            participant_id=participant_id,
                            place=place_no,
                            points_for_discipline=pts,
                        )
                    )

                idx = group_end

        max_place = len(participant_ids)

        def tie_vector(participant_id: UUID) -> tuple[int, ...]:
            counts = place_counts_map.get(participant_id, {})
            return tuple(
                counts.get(place_no, 0) for place_no in range(1, max_place + 1)
            )

        def bodyweight_value(participant_id: UUID) -> float:
            bw = participant_map[participant_id].bodyweight_kg
            return float(bw) if bw is not None else 10**12

        overall_rows = []
        for participant_id in participant_ids:
            participant = participant_map[participant_id]
            overall_rows.append(
                {
                    "participant_id": participant_id,
                    "athlete_id": participant.athlete_id,
                    "bib_no": participant.bib_no,
                    "total_points": float(points_map[participant_id]),
                    "tie_vector": tie_vector(participant_id),
                    "tie_break_value": float(participant.bodyweight_kg)
                    if participant.bodyweight_kg is not None
                    else None,
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

            self.session.add(
                OverallStanding(
                    competition_division_id=division_id,
                    participant_id=row["participant_id"],
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

            items.append(
                {
                    "participant_id": row["participant_id"],
                    "athlete_id": row["athlete_id"],
                    "bib_no": row["bib_no"],
                    "total_points": row["total_points"],
                    "place": place_no,
                    "tie_break_value": row["tie_break_value"],
                }
            )

        await self.session.commit()

        return items
