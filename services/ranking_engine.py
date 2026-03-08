from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import SessionLocal

from models.competition_division import CompetitionDivision
from models.overall_standing import OverallStanding
from models.ranking_award import RankingAward
from models.ranking_entry import RankingEntry
from models.ranking_snapshot import RankingSnapshot


class RankingEngine:
    ROLLING_DAYS = 365
    BEST_RESULTS = 8
    POLICY_VERSION = "1.2"
    MIN_RANKED_PARTICIPANTS = 6
    TOP_PLACES_LIMIT = 10

    async def process_division(self, competition_division_id):
        async with SessionLocal() as session:
            division = await session.get(CompetitionDivision, competition_division_id)
            if not division:
                raise ValueError("CompetitionDivision not found")

            awards = await self._generate_awards(session, division)
            await self._create_entries(session, awards)
            await self._refresh_ranking(
                session=session,
                division_key=division.division_key,
                format_value=division.format,
            )

            await session.commit()

    async def _generate_awards(
        self,
        session: AsyncSession,
        division: CompetitionDivision,
    ) -> list[RankingAward]:
        await session.execute(
            delete(RankingAward).where(
                RankingAward.competition_division_id == division.id
            )
        )

        res = await session.execute(
            select(OverallStanding).where(
                OverallStanding.competition_division_id == division.id
            )
        )
        standings = list(res.scalars().all())

        ranked_count = len(standings)
        if ranked_count < self.MIN_RANKED_PARTICIPANTS:
            return []

        q_effective = Decimal(str(division.q_effective))
        awards: list[RankingAward] = []
        now = datetime.utcnow()

        for standing in standings:
            place = int(standing.place)

            if place > self.TOP_PLACES_LIMIT:
                continue

            p_event = Decimal(ranked_count - (place - 1))
            s_awarded = p_event * q_effective

            award = RankingAward(
                athlete_id=standing.athlete_id,
                competition_division_id=division.id,
                overall_place=place,
                p_event=p_event,
                q_effective_applied=q_effective,
                s_awarded=s_awarded,
                policy_version=self.POLICY_VERSION,
                created_at=now,
            )
            session.add(award)
            awards.append(award)

        await session.flush()
        return awards

    async def _create_entries(
        self,
        session: AsyncSession,
        awards: list[RankingAward],
    ) -> None:
        if not awards:
            return

        division_ids = {award.competition_division_id for award in awards}

        await session.execute(
            delete(RankingEntry).where(
                RankingEntry.competition_division_id.in_(division_ids)
            )
        )

        now = datetime.utcnow()

        for award in awards:
            entry = RankingEntry(
                athlete_id=award.athlete_id,
                competition_division_id=award.competition_division_id,
                points_awarded=award.s_awarded,
                p_value=award.p_event,
                q_value=award.q_effective_applied,
                formula_version=award.policy_version,
                awarded_at=award.created_at or now,
            )
            session.add(entry)

        await session.flush()

    async def _refresh_ranking(
        self,
        session: AsyncSession,
        division_key: str,
        format_value: str,
    ) -> None:
        cutoff = datetime.utcnow() - timedelta(days=self.ROLLING_DAYS)

        entries_res = await session.execute(
            select(RankingEntry)
            .join(
                CompetitionDivision,
                CompetitionDivision.id == RankingEntry.competition_division_id,
            )
            .where(RankingEntry.awarded_at >= cutoff)
            .where(CompetitionDivision.division_key == division_key)
            .where(CompetitionDivision.format == format_value)
        )
        entries = list(entries_res.scalars().all())

        season_year = datetime.utcnow().year

        await session.execute(
            delete(RankingSnapshot).where(
                RankingSnapshot.season_year == season_year,
                RankingSnapshot.division_key == division_key,
                RankingSnapshot.format == format_value,
            )
        )

        athlete_entries: dict = {}
        for entry in entries:
            athlete_entries.setdefault(entry.athlete_id, []).append(entry)

        ranking_rows = []

        for athlete_id, rows in athlete_entries.items():
            rows.sort(
                key=lambda x: (
                    Decimal(str(x.points_awarded)),
                    x.awarded_at,
                ),
                reverse=True,
            )

            best_rows = rows[: self.BEST_RESULTS]
            total_points = sum(
                Decimal(str(r.points_awarded)) for r in best_rows
            )
            best_single = max(
                (Decimal(str(r.points_awarded)) for r in best_rows),
                default=Decimal("0"),
            )
            most_recent_best = max(
                (
                    r.awarded_at
                    for r in best_rows
                    if Decimal(str(r.points_awarded)) == best_single
                ),
                default=datetime.min,
            )

            ranking_rows.append(
                {
                    "athlete_id": athlete_id,
                    "points": total_points,
                    "best_single": best_single,
                    "most_recent_best": most_recent_best,
                }
            )

        ranking_rows.sort(
            key=lambda x: (
                x["points"],
                x["best_single"],
                x["most_recent_best"],
                str(x["athlete_id"]),
            ),
            reverse=True,
        )

        place = 1
        for row in ranking_rows:
            snapshot = RankingSnapshot(
                season_year=season_year,
                division_key=division_key,
                format=format_value,
                athlete_id=row["athlete_id"],
                points=row["points"],
                place=place,
            )
            session.add(snapshot)
            place += 1

        await session.flush()
