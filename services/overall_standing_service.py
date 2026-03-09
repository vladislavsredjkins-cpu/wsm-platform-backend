from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
import uuid
import datetime


class OverallStandingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(self, competition_division_id: uuid.UUID) -> List[OverallStanding]:
        # 1. Получаем все дисциплины дивизиона
        result = await self.db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == competition_division_id)
        )
        disciplines = result.scalars().all()
        discipline_ids = [d.id for d in disciplines]

        if not discipline_ids:
            return []

        # 2. Получаем все discipline standings
        result = await self.db.execute(
            select(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id.in_(discipline_ids))
        )
        standings = result.scalars().all()

        # 3. Агрегируем очки по участнику
        # participant_id -> {total_points, place_counts: {1: N, 2: N, ...}}
        participant_data = {}
        for s in standings:
            pid = s.participant_id
            if pid not in participant_data:
                participant_data[pid] = {
                    "total_points": Decimal(0),
                    "place_counts": {},
                    "weight_in": None,
                }
            participant_data[pid]["total_points"] += s.points_for_discipline
            place = s.place
            participant_data[pid]["place_counts"][place] = \
                participant_data[pid]["place_counts"].get(place, 0) + 1

        # 4. Получаем weight_in для тайбрейка
        result = await self.db.execute(
            select(Participant)
            .where(Participant.competition_division_id == competition_division_id)
        )
        participants = result.scalars().all()
        for p in participants:
            if p.id in participant_data:
                participant_data[p.id]["weight_in"] = p.weight_in

        # 5. Сортировка с тайбрейком
        # 1. total_points DESC
        # 2. количество 1-х мест DESC, потом 2-х мест DESC и тд
        # 3. weight_in ASC (меньший вес побеждает)
        def sort_key(item):
            pid, data = item
            place_counts = data["place_counts"]
            max_place = max(place_counts.keys()) if place_counts else 0
            places_vector = [-place_counts.get(i, 0) for i in range(1, max_place + 1)]
            weight = float(data["weight_in"]) if data["weight_in"] else 999
            return (-data["total_points"], places_vector, weight)

        sorted_participants = sorted(participant_data.items(), key=sort_key)

        # 6. Удаляем старые overall standings
        await self.db.execute(
            delete(OverallStanding)
            .where(OverallStanding.competition_division_id == competition_division_id)
        )

        # 7. Создаём новые overall standings
        result_standings = []
        for place, (pid, data) in enumerate(sorted_participants, start=1):
            tiebreak_vector = {
                str(k): v for k, v in data["place_counts"].items()
            }
            standing = OverallStanding(
                id=uuid.uuid4(),
                competition_division_id=competition_division_id,
                participant_id=pid,
                total_points=data["total_points"],
                overall_place=place,
                tiebreak_vector=tiebreak_vector,
                created_at=datetime.datetime.utcnow(),
            )
            self.db.add(standing)
            result_standings.append(standing)

        await self.db.commit()
        return result_standings