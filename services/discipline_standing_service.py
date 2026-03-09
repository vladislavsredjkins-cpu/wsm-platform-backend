from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
import uuid


class DisciplineStandingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, competition_discipline_id: uuid.UUID) -> List[DisciplineStanding]:
        result = await self.db.execute(
            select(DisciplineResult)
            .where(DisciplineResult.competition_discipline_id == competition_discipline_id)
        )
        results = result.scalars().all()
        if not results:
            return []

        def is_zero(r):
            return r.status_flag in ('DNS', 'DNF', 'DSQ') or r.primary_value is None

        def sort_key(r):
            if is_zero(r):
                return (1, Decimal(0))
            return (0, -r.primary_value)

        sorted_results = sorted(results, key=sort_key)
        n = len(sorted_results)
        place_points = {}
        place_numbers = {}

        i = 0
        while i < n:
            r = sorted_results[i]
            if is_zero(r):
                place_points[r.participant_id] = Decimal(0)
                place_numbers[r.participant_id] = i + 1
                i += 1
                continue

            j = i
            while j < n and not is_zero(sorted_results[j]) and sorted_results[j].primary_value == r.primary_value:
                j += 1

            group = sorted_results[i:j]
            group_size = len(group)
            total_pts = sum(Decimal(n - (i + k)) for k in range(group_size))
            avg_pts = total_pts / group_size

            for k, gr in enumerate(group):
                place_points[gr.participant_id] = avg_pts
                place_numbers[gr.participant_id] = i + 1
            i = j

        await self.db.execute(
            delete(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id == competition_discipline_id)
        )

        standings = []
        for r in results:
            standing = DisciplineStanding(
                id=uuid.uuid4(),
                competition_discipline_id=competition_discipline_id,
                participant_id=r.participant_id,
                place=place_numbers.get(r.participant_id, n),
                points_for_discipline=place_points.get(r.participant_id, Decimal(0)),
            )
            self.db.add(standing)
            standings.append(standing)

        await self.db.commit()
        return standings
