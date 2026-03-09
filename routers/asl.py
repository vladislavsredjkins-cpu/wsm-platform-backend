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
