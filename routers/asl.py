import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
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

router = APIRouter(prefix="/api/asl", tags=["asl"])

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
    judge_id: Optional[uuid.UUID] = None
    judge2_id: Optional[uuid.UUID] = None

class MatchResult(BaseModel):
    home_score: int
    away_score: int

@router.post("/matches")
async def create_match(data: MatchCreate, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    from datetime import date
    match_date = None
    if data.match_date:
        try:
            match_date = date.fromisoformat(data.match_date)
        except:
            match_date = None
    match = Match(
        asl_division_id=data.asl_division_id,
        home_team_id=data.home_team_id,
        away_team_id=data.away_team_id,
        match_date=match_date,
        round_number=data.round_number,
        judge_id=data.judge_id,
        judge2_id=data.judge2_id,
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

@router.delete("/matches/{match_id}")
async def delete_match(match_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                       current_user=Depends(get_current_user)):
    from models.match_discipline_result import MatchDisciplineResult
    await db.execute(
        delete(MatchDisciplineResult).where(MatchDisciplineResult.match_id == match_id)
    )
    match = await db.get(Match, match_id)
    if match:
        await db.delete(match)
    await db.commit()
    return {"ok": True}

@router.get("/matches/my")
async def get_my_matches(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from models.judge import Judge
    from sqlalchemy import or_
    jr = await db.execute(select(Judge).where(Judge.user_id == current_user.id))
    judge = jr.scalar_one_or_none()
    if not judge:
        return []
    res = await db.execute(
        select(Match).where(or_(Match.judge_id == judge.id, Match.judge2_id == judge.id))
    )
    matches = res.scalars().all()
    # Добавляем поле my_side чтобы фронтенд знал какую колонку показывать
    result = []
    for m in matches:
        d = {
            "id": str(m.id),
            "asl_division_id": str(m.asl_division_id) if m.asl_division_id else None,
            "home_team_id": str(m.home_team_id),
            "away_team_id": str(m.away_team_id),
            "home_score": m.home_score,
            "away_score": m.away_score,
            "status": m.status,
            "round_number": m.round_number,
            "judge_id": str(m.judge_id) if m.judge_id else None,
            "judge2_id": str(m.judge2_id) if m.judge2_id else None,
            "my_side": "home" if m.judge_id == judge.id else "away",
        }
        result.append(d)
    return result

@router.get("/matches/{match_id}")
async def get_match(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    match = await db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Not found")
    return match


class DisciplineResultCreate(BaseModel):
    discipline_name: str
    home_result: float
    away_result: float
    result_type: str = 'higher_wins'  # higher_wins / lower_wins
    unit: str = 'kg'

@router.get("/matches/{match_id}/disciplines")
async def get_match_disciplines(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.match_discipline_result import MatchDisciplineResult
    result = await db.execute(
        select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == match_id)
    )
    return result.scalars().all()

@router.post("/matches/{match_id}/disciplines")
async def set_discipline_result(match_id: uuid.UUID, data: DisciplineResultCreate,
                                db: AsyncSession = Depends(get_db),
                                current_user=Depends(get_current_user)):
    from models.match_discipline_result import MatchDisciplineResult
    # Удаляем старый если есть
    existing = await db.execute(
        select(MatchDisciplineResult).where(
            MatchDisciplineResult.match_id == match_id,
            MatchDisciplineResult.discipline_name == data.discipline_name
        )
    )
    old = existing.scalar_one_or_none()
    if old:
        await db.delete(old)

    # Определяем победителя
    if data.result_type == 'lower_wins':
        winner = 'home' if data.home_result < data.away_result else ('away' if data.away_result < data.home_result else 'draw')
    else:
        winner = 'home' if data.home_result > data.away_result else ('away' if data.away_result > data.home_result else 'draw')

    dr = MatchDisciplineResult(
        match_id=match_id,
        discipline_name=data.discipline_name,
        home_result=data.home_result,
        away_result=data.away_result,
        result_type=data.result_type,
        unit=data.unit,
        winner=winner
    )
    db.add(dr)

    # Пересчитываем счёт матча
    match = await db.get(Match, match_id)
    all_results = await db.execute(
        select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == match_id)
    )
    results_list = all_results.scalars().all()
    results_list = [r for r in results_list if r.discipline_name != data.discipline_name] + [dr]

    home_score = sum(1 for r in results_list if r.winner == 'home')
    away_score = sum(1 for r in results_list if r.winner == 'away')
    match.home_score = home_score
    match.away_score = away_score
    if len(results_list) >= 5:
        match.status = 'completed'

    await db.commit()
    return {"winner": winner, "home_score": home_score, "away_score": away_score}
