from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.participant import Participant
import uuid
import datetime


class DisciplineStandingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, competition_discipline_id: uuid.UUID) -> List[DisciplineStanding]:
        # 1. Получаем все результаты по дисциплине
        result = await self.db.execute(
            select(DisciplineResult)
            .where(DisciplineResult.competition_discipline_id == competition_discipline_id)
        )
        results = result.scalars().all()

        if not results:
            return []

        # 2. Сортируем — zero results в конец, остальные по убыванию result_value
        def sort_key(r):
            if r.is_zero or r.result_value is None:
                return (1, Decimal(0))
            return (0, -r.result_value)

        sorted_results = sorted(results, key=sort_key)

        # 3. Считаем места с учётом ничьей (draw)
        n = len(sorted_results)
        place_points = {}  # participant_id -> points
        place_numbers = {}  # participant_id -> place

        i = 0
        while i < n:
            r = sorted_results[i]

            # zero result — 0 очков
            if r.is_zero or r.result_value is None:
                place_points[r.participant_id] = Decimal(0)
                place_numbers[r.participant_id] = i + 1
                i += 1
                continue

            # ищем группу с одинаковым результатом (draw)
            j = i
            while j < n and not sorted_results[j].is_zero and sorted_results[j].result_value == r.result_value:
                j += 1

            group = sorted_results[i:j]
            group_size = len(group)

            # очки за места в группе суммируются и делятся поровну
            # места: i+1, i+2, ... i+group_size (1-based)
            # очки за место = N - (place - 1) где N = общее число участников
            total_pts = sum(Decimal(n - (i + k)) for k in range(group_size))
            avg_pts = total_pts / group_size

            for k, gr in enumerate(group):
                place_points[gr.participant_id] = avg_pts
                place_numbers[gr.participant_id] = i + 1

            i = j

        # 4. Удаляем старые standings
        await self.db.execute(
            delete(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id == competition_discipline_id)
        )

        # 5. Создаём новые standings
        standings = []
        for r in results:
            standing = DisciplineStanding(
                id=uuid.uuid4(),
                competition_discipline_id=competition_discipline_id,
                participant_id=r.participant_id,
                place=place_numbers.get(r.participant_id, n),
                points_for_discipline=place_points.get(r.participant_id, Decimal(0)),
                created_at=datetime.datetime.utcnow(),
            )
            self.db.add(standing)
            standings.append(standing)

        await self.db.commit()
        return standings