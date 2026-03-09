from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.competition_division import CompetitionDivision
from models.competition_division_q import CompetitionDivisionQ
from models.competition_division_snapshot import CompetitionDivisionSnapshot
from models.overall_standing import OverallStanding
from models.discipline_standing import DisciplineStanding
from models.discipline_result import DisciplineResult
from models.participant import Participant
from models.competition_discipline import CompetitionDiscipline
import uuid
import datetime


class FinalizationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate(self, competition_division_id: uuid.UUID) -> dict:
        errors = []

        # 1. Проверяем division существует
        result = await self.db.execute(
            select(CompetitionDivision)
            .where(CompetitionDivision.id == competition_division_id)
        )
        division = result.scalar_one_or_none()
        if not division:
            return {"valid": False, "errors": ["Division not found"]}

        # 2. Проверяем уже не locked
        if division.is_locked:
            return {"valid": False, "errors": ["Division already locked"]}

        # 3. Проверяем минимум 6 атлетов
        result = await self.db.execute(
            select(func.count(Participant.id))
            .where(Participant.competition_division_id == competition_division_id)
        )
        athlete_count = result.scalar()
        if athlete_count < 6:
            errors.append(f"Division has {athlete_count} athletes — minimum 6 required for ranking")

        # 4. Проверяем Q coefficient существует
        result = await self.db.execute(
            select(CompetitionDivisionQ)
            .where(CompetitionDivisionQ.competition_division_id == competition_division_id)
        )
        division_q = result.scalar_one_or_none()
        if not division_q:
            errors.append("Q coefficient not set for this division")

        # 5. Проверяем overall standings существуют
        result = await self.db.execute(
            select(func.count(OverallStanding.id))
            .where(OverallStanding.competition_division_id == competition_division_id)
        )
        standings_count = result.scalar()
        if standings_count == 0:
            errors.append("Overall standings not calculated yet")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "athlete_count": athlete_count,
            "standings_count": standings_count,
            "q_set": division_q is not None,
        }

    async def lock(self, competition_division_id: uuid.UUID) -> CompetitionDivision:
        # 1. Валидируем
        validation = await self.validate(competition_division_id)
        if not validation["valid"]:
            raise ValueError(f"Cannot lock division: {validation['errors']}")

        # 2. Получаем division
        result = await self.db.execute(
            select(CompetitionDivision)
            .where(CompetitionDivision.id == competition_division_id)
        )
        division = result.scalar_one()

        # 3. Создаём snapshot
        await self._create_snapshot(competition_division_id)

        # 4. Лочим division
        division.is_locked = True
        division.locked_at = datetime.datetime.utcnow()
        division.status = "LOCKED"

        await self.db.commit()
        return division

    async def _create_snapshot(self, competition_division_id: uuid.UUID):
        # Получаем Q
        result = await self.db.execute(
            select(CompetitionDivisionQ)
            .where(CompetitionDivisionQ.competition_division_id == competition_division_id)
        )
        division_q = result.scalar_one_or_none()

        # Получаем participants
        result = await self.db.execute(
            select(Participant)
            .where(Participant.competition_division_id == competition_division_id)
        )
        participants = result.scalars().all()

        # Получаем overall standings
        result = await self.db.execute(
            select(OverallStanding)
            .where(OverallStanding.competition_division_id == competition_division_id)
            .order_by(OverallStanding.overall_place)
        )
        overall = result.scalars().all()

        # Получаем discipline standings
        result = await self.db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == competition_division_id)
        )
        disciplines = result.scalars().all()
        discipline_ids = [d.id for d in disciplines]

        result = await self.db.execute(
            select(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id.in_(discipline_ids))
        )
        disc_standings = result.scalars().all()

        # Собираем snapshot data
        snapshot_data = {
            "participants": [
                {"id": str(p.id), "athlete_id": str(p.athlete_id), "weight_in": float(p.weight_in) if p.weight_in else None}
                for p in participants
            ],
            "overall_standings": [
                {"participant_id": str(o.participant_id), "place": o.overall_place, "total_points": float(o.total_points)}
                for o in overall
            ],
            "discipline_standings": [
                {"participant_id": str(d.participant_id), "discipline_id": str(d.competition_discipline_id), "place": d.place, "points": float(d.points_for_discipline)}
                for d in disc_standings
            ],
            "snapshot_at": datetime.datetime.utcnow().isoformat(),
        }

        snapshot = CompetitionDivisionSnapshot(
            id=uuid.uuid4(),
            competition_division_id=competition_division_id,
            snapshot_data=snapshot_data,
            q_effective=division_q.q_effective if division_q else None,
            created_at=datetime.datetime.utcnow(),
            version=1,
        )
        self.db.add(snapshot)