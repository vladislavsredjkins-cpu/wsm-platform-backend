import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import date
from db.database import get_db
from models.match import Match
from models.match_discipline_result import MatchDisciplineResult
from models.team_standing import TeamStanding
from auth.dependencies import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])

class MatchCreate(BaseModel):
    asl_division_id: Optional[uuid.UUID] = None
    competition_division_id: Optional[uuid.UUID] = None
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    match_date: Optional[date] = None
    round_number: Optional[int] = None

class MatchUpdate(BaseModel):
    match_date: Optional[date] = None
    status: Optional[str] = None
    round_number: Optional[int] = None

class DisciplineResultCreate(BaseModel):
    discipline_name: str
    home_result: Optional[float] = None
    away_result: Optional[float] = None
    winner: Optional[str] = None  # home / away

class ScoreSubmit(BaseModel):
    discipline_results: list[DisciplineResultCreate]

def update_standings(standings_home: TeamStanding, standings_away: TeamStanding,
                     home_score: int, away_score: int,
                     disciplines_won_home: int, disciplines_won_away: int):
    standings_home.matches_played += 1
    standings_away.matches_played += 1
    standings_home.disciplines_won += disciplines_won_home
    standings_home.disciplines_lost += disciplines_won_away
    standings_away.disciplines_won += disciplines_won_away
    standings_away.disciplines_lost += disciplines_won_home
    if home_score > away_score:
        standings_home.wins += 1
        standings_home.points += 3
        standings_away.losses += 1
    elif away_score > home_score:
        standings_away.wins += 1
        standings_away.points += 3
        standings_home.losses += 1
    else:
        standings_home.points += 1
        standings_away.points += 1

@router.get("/division/{division_id}")
async def list_matches(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Match).where(
            (Match.competition_division_id == division_id) |
            (Match.asl_division_id == division_id)
        ).order_by(Match.round_number, Match.match_date)
    )
    return result.scalars().all()

@router.get("/{match_id}")
async def get_match(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.get("/{match_id}/results")
async def get_match_results(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == match_id)
    )
    return result.scalars().all()

@router.post("/")
async def create_match(data: MatchCreate, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    match = Match(**data.dict(), status="scheduled", home_score=0, away_score=0)
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match

@router.patch("/{match_id}")
async def update_match(match_id: uuid.UUID, data: MatchUpdate,
                       db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for k, v in data.dict(exclude_none=True).items():
        setattr(match, k, v)
    await db.commit()
    await db.refresh(match)
    return match

@router.post("/{match_id}/submit-score")
async def submit_score(match_id: uuid.UUID, data: ScoreSubmit,
                       db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if len(data.discipline_results) != 5:
        raise HTTPException(status_code=400, detail="Exactly 5 discipline results required")

    # Удаляем старые результаты если есть
    old = await db.execute(
        select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == match_id)
    )
    for r in old.scalars().all():
        await db.delete(r)

    home_score = 0
    away_score = 0
    for dr in data.discipline_results:
        if dr.winner == "home":
            home_score += 1
        elif dr.winner == "away":
            away_score += 1
        result = MatchDisciplineResult(match_id=match_id, **dr.dict())
        db.add(result)

    match.home_score = home_score
    match.away_score = away_score
    match.status = "completed"

    # Обновляем standings
    div_id = match.asl_division_id or match.competition_division_id

    async def get_or_create_standing(team_id):
        is_asl = match.asl_division_id is not None
        if is_asl:
            res = await db.execute(
                select(TeamStanding).where(
                    TeamStanding.team_id == team_id,
                    TeamStanding.asl_division_id == div_id
                )
            )
        else:
            res = await db.execute(
                select(TeamStanding).where(
                    TeamStanding.team_id == team_id,
                    TeamStanding.competition_division_id == div_id
                )
            )
        s = res.scalar_one_or_none()
        if not s:
            s = TeamStanding(
                team_id=team_id,
                asl_division_id=div_id if is_asl else None,
                competition_division_id=None if is_asl else div_id,
                matches_played=0, wins=0, losses=0,
                disciplines_won=0, disciplines_lost=0, points=0
            )
            db.add(s)
        return s

    s_home = await get_or_create_standing(match.home_team_id)
    s_away = await get_or_create_standing(match.away_team_id)
    update_standings(s_home, s_away, home_score, away_score, home_score, away_score)

    await db.commit()
    return {
        "match_id": str(match_id),
        "home_score": home_score,
        "away_score": away_score,
        "status": "completed"
    }

@router.get("/standings/{division_id}")
async def get_standings(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamStanding)
        .where(TeamStanding.competition_division_id == division_id)
        .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
    )
    return result.scalars().all()
