from uuid import UUID
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from db.database import SessionLocal
from models.athlete import Athlete
from models.competition import Competition
from models.competition_division import CompetitionDivision
from models.overall_standing import OverallStanding
from models.participant import Participant
from models.ranking_point import RankingPoint
from models.ranking_snapshot import RankingSnapshot


router = APIRouter(tags=["ranking"])


DivisionKey = Literal["MEN", "WOMEN", "PARA"]
CompetitionFormat = Literal["CLASSIC", "PARA", "RELAY", "TEAM_BATTLE"]


class FinalizeOut(BaseModel):
    competition_id: UUID
    season_year: int
    rows_written: int


class RankingItem(BaseModel):
    athlete_id: UUID
    first_name: str
    last_name: str
    country: str
    points: float


class RankingOut(BaseModel):
    division: DivisionKey
    format: CompetitionFormat
    season_year: int
    limit: int
    offset: int
    items: list[RankingItem]


class RankingSnapshotOut(BaseModel):
    snapshot_created: int


@router.get("/ranking", response_model=RankingOut)
async def get_ranking(
    division: DivisionKey = Query("MEN"),
    format: CompetitionFormat = Query("CLASSIC"),
    season_year: int = Query(..., ge=2000, le=2100),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    async with SessionLocal() as session:
        stmt = (
            select(
                Athlete.id.label("athlete_id"),
                Athlete.first_name,
                Athlete.last_name,
                Athlete.country,
                func.sum(RankingPoint.points).label("points"),
            )
            .join(RankingPoint, RankingPoint.athlete_id == Athlete.id)
            .where(
                RankingPoint.season_year == season_year,
                RankingPoint.division_key == division,
                RankingPoint.format == format,
            )
            .group_by(Athlete.id, Athlete.first_name, Athlete.last_name, Athlete.country)
            .order_by(func.sum(RankingPoint.points).desc())
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(stmt)
        rows = result.all()

        items = [
            RankingItem(
                athlete_id=row.athlete_id,
                first_name=row.first_name,
                last_name=row.last_name,
                country=row.country,
                points=float(row.points) if row.points is not None else 0.0,
            )
            for row in rows
        ]

        return RankingOut(
            division=division,
            format=format,
            season_year=season_year,
            limit=limit,
            offset=offset,
            items=items,
        )


@router.post("/ranking/snapshot", response_model=RankingSnapshotOut)
async def create_ranking_snapshot(
    season_year: int,
    division: DivisionKey,
    format: CompetitionFormat,
):
    async with SessionLocal() as session:
        stmt = (
            select(
                RankingPoint.athlete_id,
                func.sum(RankingPoint.points).label("points"),
            )
            .where(
                RankingPoint.season_year == season_year,
                RankingPoint.division_key == division,
                RankingPoint.format == format,
            )
            .group_by(RankingPoint.athlete_id)
            .order_by(func.sum(RankingPoint.points).desc())
        )

        result = await session.execute(stmt)
        rows = result.all()

        place = 1
        for row in rows:
            session.add(
                RankingSnapshot(
                    season_year=season_year,
                    division_key=division,
                    format=format,
                    athlete_id=row.athlete_id,
                    points=float(row.points),
                    place=place,
                )
            )
            place += 1

        await session.commit()

        return RankingSnapshotOut(snapshot_created=place - 1)


@router.post("/competitions/{competition_id}/finalize", response_model=FinalizeOut)
async def finalize_competition(
    competition_id: UUID,
    season_year: int = Query(..., ge=2000, le=2100),
):
    async with SessionLocal() as session:
        competition_res = await session.execute(
            select(Competition).where(Competition.id == competition_id)
        )
        competition = competition_res.scalar_one_or_none()
        if not competition:
            raise HTTPException(status_code=404, detail="Competition not found")

        q = float(competition.coefficient_q)

        division_res = await session.execute(
            select(CompetitionDivision).where(
                CompetitionDivision.competition_id == competition_id
            )
        )
        divisions = list(division_res.scalars().all())

        rows_written = 0

        for division in divisions:
            division_id = division.id

            if division.status != "LOCKED":
                raise HTTPException(
                    status_code=400,
                    detail="Division must be LOCKED before finalize",
                )

            overall_res = await session.execute(
                select(OverallStanding).where(
                    OverallStanding.competition_division_id == division_id
                )
            )
            overall_rows = list(overall_res.scalars().all())

            if not overall_rows:
                continue

            for row in overall_rows:
                participant = await session.get(Participant, row.participant_id)
                if not participant:
                    continue

                raw_points = float(row.total_points)
                final_points = raw_points * q

                existing_res = await session.execute(
                    select(RankingPoint).where(
                        RankingPoint.competition_id == competition_id,
                        RankingPoint.division_id == division_id,
                        RankingPoint.athlete_id == participant.athlete_id,
                    )
                )
                existing = existing_res.scalar_one_or_none()

                if existing:
                    existing.season_year = season_year
                    existing.division_key = division.division_key
                    existing.format = division.format
                    existing.points = final_points
                else:
                    session.add(
                        RankingPoint(
                            season_year=season_year,
                            competition_id=competition_id,
                            division_id=division_id,
                            athlete_id=participant.athlete_id,
                            division_key=division.division_key,
                            format=division.format,
                            points=final_points,
                        )
                    )

                rows_written += 1

        await session.commit()

        return FinalizeOut(
            competition_id=competition_id,
            season_year=season_year,
            rows_written=rows_written,
        )
