from datetime import datetime, timedelta
from sqlalchemy import select, delete
from db.database import SessionLocal

from models.overall_standing import OverallStanding
from models.competition_division import CompetitionDivision
from models.ranking_award import RankingAward
from models.ranking_entry import RankingEntry
from models.ranking import Ranking


class RankingEngine:

    ROLLING_DAYS = 365
    BEST_RESULTS = 8

    # --------------------------------
    # PUBLIC ENTRYPOINT
    # --------------------------------

    async def process_division(self, competition_division_id):

        async with SessionLocal() as session:

            awards = await self._generate_awards(session, competition_division_id)

            await self._create_entries(session, awards)

            division = await session.get(CompetitionDivision, competition_division_id)

            await self._refresh_ranking(session, division.division_scope)

            await session.commit()

    # --------------------------------
    # STEP 1 — CREATE AWARDS
    # --------------------------------

    async def _generate_awards(self, session, division_id):

        res = await session.execute(
            select(OverallStanding)
            .where(OverallStanding.competition_division_id == division_id)
        )

        standings = res.scalars().all()

        division = await session.get(CompetitionDivision, division_id)

        Q = division.q_effective

        N = len(standings)

        awards = []

        for s in standings:

            place = s.place

            if place > 10:
                continue

            P = N - (place - 1)

            S = P * Q

            award = RankingAward(
                athlete_id=s.athlete_id,
                competition_division_id=division_id,
                overall_place=place,
                p_event=P,
                q_effective_applied=Q,
                s_awarded=S,
                policy_version="1.2",
                created_at=datetime.utcnow()
            )

            session.add(award)

            awards.append(award)

        return awards

    # --------------------------------
    # STEP 2 — CREATE ENTRIES
    # --------------------------------

    async def _create_entries(self, session, awards):

        for award in awards:

            entry = RankingEntry(
                athlete_id=award.athlete_id,
                competition_division_id=award.competition_division_id,
                points_awarded=award.s_awarded,
                p_value=award.p_event,
                q_value=award.q_effective_applied,
                formula_version=award.policy_version,
                awarded_at=award.created_at
            )

            session.add(entry)

    # --------------------------------
    # STEP 3 — REFRESH RANKING
    # --------------------------------

    async def _refresh_ranking(self, session, scope):

        cutoff = datetime.utcnow() - timedelta(days=self.ROLLING_DAYS)

        res = await session.execute(
            select(RankingEntry)
            .where(RankingEntry.awarded_at >= cutoff)
            .where(RankingEntry.scope == scope)
        )

        entries = res.scalars().all()

        athlete_map = {}

        for e in entries:
            athlete_map.setdefault(e.athlete_id, []).append(e)

        ranking_rows = []

        for athlete_id, rows in athlete_map.items():

            rows.sort(key=lambda x: x.points_awarded, reverse=True)

            best = rows[:self.BEST_RESULTS]

            total = sum(r.points_awarded for r in best)

            ranking_rows.append(
                (athlete_id, total, len(best))
            )

        ranking_rows.sort(key=lambda x: x[1], reverse=True)

        await session.execute(delete(Ranking).where(Ranking.scope == scope))

        place = 1

        for athlete_id, total, count in ranking_rows:

            row = Ranking(
                athlete_id=athlete_id,
                ranking_scope=scope,
                total_points=total,
                rated_events_count=count,
                current_place=place,
                updated_at=datetime.utcnow()
            )

            session.add(row)

            place += 1
