from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.overall_standing import OverallStanding
from models.competition_division_q import CompetitionDivisionQ
from models.competition_division import CompetitionDivision
from models.ranking_award import RankingAward
from models.ranking_entry import RankingEntry
from models.participant import Participant
import uuid
import datetime


# Таблица P — очки за место
P_TABLE = {
    1: 10, 2: 9, 3: 8, 4: 7, 5: 6,
    6: 5, 7: 4, 8: 3, 9: 2, 10: 1
}

MIN_ATHLETES = 6
MAX_RANKED_PLACE = 10


class RankingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_division(self, competition_division_id: uuid.UUID) -> List[RankingAward]:
        # 1. Получаем division
        result = await self.db.execute(
            select(CompetitionDivision)
            .where(CompetitionDivision.id == competition_division_id)
        )
        division = result.scalar_one_or_none()
        if not division:
            raise ValueError(f"Division {competition_division_id} not found")

        # 2. Проверяем что division locked
        if not division.is_locked:
            raise ValueError("Division must be locked before ranking awards can be processed")

        # 3. Получаем Q effective
        result = await self.db.execute(
            select(CompetitionDivisionQ)
            .where(CompetitionDivisionQ.competition_division_id == competition_division_id)
        )
        division_q = result.scalar_one_or_none()
        if not division_q:
            raise ValueError("Division Q not found — cannot process ranking")

        q_effective = division_q.q_effective

        # 4. Получаем overall standings
        result = await self.db.execute(
            select(OverallStanding)
            .where(OverallStanding.competition_division_id == competition_division_id)
            .order_by(OverallStanding.overall_place)
        )
        standings = result.scalars().all()

        # 5. Проверяем минимум 6 атлетов
        if len(standings) < MIN_ATHLETES:
            return []

        # 6. Получаем athlete_id для каждого participant
        participant_ids = [s.participant_id for s in standings]
        result = await self.db.execute(
            select(Participant)
            .where(Participant.id.in_(participant_ids))
        )
        participants = result.scalars().all()
        participant_map = {p.id: p.athlete_id for p in participants}

        # 7. Создаём ranking_awards и ranking_entries
        awards = []
        now = datetime.datetime.utcnow()

        for standing in standings:
            place = standing.overall_place

            # TOP-10 rule
            if place > MAX_RANKED_PLACE:
                break

            p_value = P_TABLE.get(place, 0)
            if p_value == 0:
                continue

            s_awarded = Decimal(str(p_value)) * q_effective
            athlete_id = participant_map.get(standing.participant_id)

            if not athlete_id:
                continue

            # Создаём award
            award = RankingAward(
                id=uuid.uuid4(),
                athlete_id=athlete_id,
                competition_division_id=competition_division_id,
                overall_place=place,
                p_value=p_value,
                q_effective_applied=q_effective,
                s_awarded=s_awarded,
                policy_version="1.0",
                created_at=now,
            )
            self.db.add(award)
            awards.append(award)

            # Создаём entry
            entry = RankingEntry(
                id=uuid.uuid4(),
                athlete_id=athlete_id,
                ranking_award_id=award.id,
                division_key=division.division_key,
                season_year=now.year,
                points=s_awarded,
                awarded_at=now,
            )
            self.db.add(entry)

        await self.db.commit()
        return awards

    async def get_ranking(self, division_key: str, season_year: int) -> List[dict]:
        # Rolling 365 дней
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=365)

        result = await self.db.execute(
            select(RankingEntry)
            .where(
                RankingEntry.division_key == division_key,
                RankingEntry.awarded_at >= cutoff_date,
            )
            .order_by(RankingEntry.awarded_at.desc())
        )
        entries = result.scalars().all()

        # Группируем по атлету — топ 8 результатов
        athlete_entries = {}
        for entry in entries:
            aid = entry.athlete_id
            if aid not in athlete_entries:
                athlete_entries[aid] = []
            athlete_entries[aid].append(entry)

        # Считаем итоговые очки
        ranking = []
        for athlete_id, athlete_entries_list in athlete_entries.items():
            sorted_entries = sorted(athlete_entries_list, key=lambda e: e.points, reverse=True)
            top_8 = sorted_entries[:8]
            total_points = sum(e.points for e in top_8)
            best_result = top_8[0].points if top_8 else Decimal(0)
            best_result_date = top_8[0].awarded_at if top_8 else None

            ranking.append({
                "athlete_id": str(athlete_id),
                "total_points": float(total_points),
                "best_result": float(best_result),
                "best_result_date": best_result_date,
                "competitions_count": len(top_8),
            })

        # Сортировка: total_points DESC, best_result DESC, best_result_date ASC
        ranking.sort(key=lambda x: (
            -x["total_points"],
            -x["best_result"],
            x["best_result_date"] or datetime.datetime.max,
        ))

        # Добавляем позицию
        for i, r in enumerate(ranking, start=1):
            r["position"] = i

        return ranking