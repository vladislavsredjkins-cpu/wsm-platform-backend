import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from db.database import get_db
from models.asl_league import ASLLeague
from models.asl_division import ASLDivision
from models.asl_team_division import ASLTeamDivision
from models.team import Team
from models.match import Match
from models.team_standing import TeamStanding
from auth.dependencies import get_current_user

router = APIRouter(prefix="/asl", tags=["asl"])

class LeagueCreate(BaseModel):
    name: str
    season: Optional[str] = None

class DivisionCreate(BaseModel):
    league_id: uuid.UUID
    name: str
    region: Optional[str] = None
    max_teams: Optional[int] = 4

class TeamDivisionAdd(BaseModel):
    team_id: uuid.UUID

@router.get("/leagues")
async def list_leagues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ASLLeague).order_by(ASLLeague.season.desc()))
    return result.scalars().all()

@router.post("/leagues")
async def create_league(data: LeagueCreate, db: AsyncSession = Depends(get_db),
                        current_user=Depends(get_current_user)):
    league = ASLLeague(**data.dict(), status="active")
    db.add(league)
    await db.commit()
    await db.refresh(league)
    return league

@router.get("/leagues/{league_id}")
async def get_league(league_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    league = await db.get(ASLLeague, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league

@router.get("/divisions")
async def list_divisions(league_id: Optional[uuid.UUID] = None, db: AsyncSession = Depends(get_db)):
    q = select(ASLDivision)
    if league_id:
        q = q.where(ASLDivision.league_id == league_id)
    result = await db.execute(q.order_by(ASLDivision.name))
    return result.scalars().all()

@router.post("/divisions")
async def create_division(data: DivisionCreate, db: AsyncSession = Depends(get_db),
                          current_user=Depends(get_current_user)):
    division = ASLDivision(**data.dict())
    db.add(division)
    await db.commit()
    await db.refresh(division)
    return division

@router.get("/divisions/{division_id}/detail")
async def get_division(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    division = await db.get(ASLDivision, division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    return division

@router.post("/divisions/{division_id}/teams")
async def add_team_to_division(division_id: uuid.UUID, data: TeamDivisionAdd,
                                db: AsyncSession = Depends(get_db),
                                current_user=Depends(get_current_user)):
    division = await db.get(ASLDivision, division_id)
    if not division:
        raise HTTPException(status_code=404, detail="Division not found")
    existing = await db.execute(
        select(ASLTeamDivision).where(
            ASLTeamDivision.division_id == division_id,
            ASLTeamDivision.team_id == data.team_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Team already in division")
    count = await db.execute(
        select(ASLTeamDivision).where(ASLTeamDivision.division_id == division_id)
    )
    if len(count.scalars().all()) >= division.max_teams:
        raise HTTPException(status_code=400, detail=f"Division full (max {division.max_teams} teams)")
    td = ASLTeamDivision(division_id=division_id, team_id=data.team_id)
    db.add(td)
    await db.commit()
    return {"status": "added", "division_id": str(division_id), "team_id": str(data.team_id)}

@router.get("/divisions/{division_id}/teams")
async def get_division_teams(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ASLTeamDivision).where(ASLTeamDivision.division_id == division_id)
    )
    tds = result.scalars().all()
    teams = []
    for td in tds:
        team = await db.get(Team, td.team_id)
        if team:
            teams.append(team)
    return teams

@router.get("/divisions/{division_id}/standings")
async def get_division_standings(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamStanding)
        .where(TeamStanding.asl_division_id == division_id)
        .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
    )
    return result.scalars().all()

@router.get("/divisions/{division_id}/matches")
async def get_division_matches(division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Match)
        .where(Match.asl_division_id == division_id)
        .order_by(Match.round_number, Match.match_date)
    )
    return result.scalars().all()

class MatchCreate(BaseModel):
    asl_division_id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    match_date: Optional[str] = None
    round_number: Optional[int] = None

class MatchResult(BaseModel):
    home_score: int
    away_score: int

@router.post("/matches")
async def create_match(data: MatchCreate, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    match = Match(
        asl_division_id=data.asl_division_id,
        home_team_id=data.home_team_id,
        away_team_id=data.away_team_id,
        match_date=data.match_date,
        round_number=data.round_number,
        status="scheduled"
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match

@router.patch("/matches/{match_id}/result")
async def set_match_result(match_id: uuid.UUID, data: MatchResult,
                           db: AsyncSession = Depends(get_db),
                           current_user=Depends(get_current_user)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.home_score = data.home_score
    match.away_score = data.away_score
    match.status = "completed"

    # Обновляем standings
    async def get_or_create_standing(team_id):
        result = await db.execute(
            select(TeamStanding).where(
                TeamStanding.asl_division_id == match.asl_division_id,
                TeamStanding.team_id == team_id
            )
        )
        s = result.scalar_one_or_none()
        if not s:
            s = TeamStanding(asl_division_id=match.asl_division_id, team_id=team_id)
            db.add(s)
        return s

    home_s = await get_or_create_standing(match.home_team_id)
    away_s = await get_or_create_standing(match.away_team_id)

    home_s.matches_played += 1
    away_s.matches_played += 1
    home_s.disciplines_won += data.home_score
    home_s.disciplines_lost += data.away_score
    away_s.disciplines_won += data.away_score
    away_s.disciplines_lost += data.home_score

    if data.home_score > data.away_score:
        home_s.wins += 1; home_s.points += 3
        away_s.losses += 1
    elif data.away_score > data.home_score:
        away_s.wins += 1; away_s.points += 3
        home_s.losses += 1
    else:
        home_s.points += 1; away_s.points += 1

    await db.commit()
    return {"status": "ok", "home_score": data.home_score, "away_score": data.away_score}

@router.get("/matches/{match_id}")
async def get_match(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Not found")
    return match

