from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy as sa
from db.database import SessionLocal

from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import competitions, divisions, athletes, ranking, disciplines, participants, results, auth, judges, organizers, coaches, teams, matches, asl

app = FastAPI(title="World Strongman Platform API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("uploads/athletes").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(competitions.router)
app.include_router(divisions.router)
app.include_router(athletes.router)
app.include_router(ranking.router)
app.include_router(disciplines.router)
app.include_router(participants.router)
app.include_router(results.router)
app.include_router(auth.router)
app.include_router(judges.router)
app.include_router(organizers.router)
app.include_router(coaches.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(asl.router)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-test")
async def db_test():
    async with SessionLocal() as session:
        result = await session.execute(sa.text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import select, desc
from models.athlete import Athlete

templates = Jinja2Templates(directory="templates")

@app.get("/athletes/{athlete_id}/profile")
async def athlete_profile(athlete_id: str, request: Request):
    from db.database import SessionLocal
    import uuid
    async with SessionLocal() as db:
        athlete = await db.get(Athlete, uuid.UUID(athlete_id))
        if not athlete:
            return {"error": "Athlete not found"}

        # Ranking
        ranking = None
        try:
            from models.ranking import Ranking
            r = await db.execute(
                select(Ranking).where(Ranking.athlete_id == uuid.UUID(athlete_id))
            )
            ranking = r.scalar_one_or_none()
        except:
            pass

        # Achievements - топ результаты
        achievements = []
        try:
            from models.result import Result
            from models.participant import Participant
            from models.competition_division import CompetitionDivision
            from models.competition import Competition
            from sqlalchemy.orm import selectinload
            res = await db.execute(
                select(Result)
                .join(Participant, Result.participant_id == Participant.id)
                .where(Participant.athlete_id == uuid.UUID(athlete_id))
                .order_by(desc(Result.points))
                .limit(5)
            )
            raw = res.scalars().all()
            for r in raw:
                participant = await db.get(Participant, r.participant_id)
                div = await db.get(CompetitionDivision, participant.competition_division_id)
                comp = await db.get(Competition, div.competition_id)
                achievements.append({
                    "competition_name": comp.name,
                    "division_name": div.name if hasattr(div, 'name') else "Division",
                    "result": r.points,
                })
        except:
            pass

        # Upcoming competitions
        upcoming = []
        try:
            from models.participant import Participant
            from models.competition_division import CompetitionDivision
            from models.competition import Competition
            import datetime
            parts = await db.execute(
                select(Participant).where(Participant.athlete_id == uuid.UUID(athlete_id))
            )
            for p in parts.scalars().all():
                div = await db.get(CompetitionDivision, p.competition_division_id)
                if div:
                    comp = await db.get(Competition, div.competition_id)
                    if comp and hasattr(comp, 'date') and comp.date and comp.date >= datetime.date.today():
                        upcoming.append({
                            "competition_name": comp.name,
                            "location": getattr(comp, 'location', ''),
                            "division_name": getattr(div, 'name', 'Division'),
                            "date": comp.date,
                        })
        except:
            pass

        # Sponsors
        sponsors = []
        try:
            from models.athlete_sponsor import AthleteSponsor
            sp = await db.execute(
                select(AthleteSponsor).where(AthleteSponsor.athlete_id == uuid.UUID(athlete_id)).limit(3)
            )
            sponsors = sp.scalars().all()
        except:
            pass

        return templates.TemplateResponse("athlete_profile.html", {
            "request": request,
            "athlete": athlete,
            "ranking": ranking,
            "achievements": achievements,
            "upcoming": upcoming,
            "upcoming_count": len(upcoming),
            "sponsors": sponsors,
        })


@app.get("/athletes-list")
async def athletes_list(request: Request):
    from sqlalchemy import select
    from models.athlete import Athlete
    async with SessionLocal() as db:
        result = await db.execute(select(Athlete).order_by(Athlete.last_name))
        athletes = result.scalars().all()
    return templates.TemplateResponse("athletes_list.html", {
        "request": request,
        "athletes": athletes,
    })


@app.get("/judges/{judge_id}/profile")
async def judge_profile(judge_id: str, request: Request):
    import uuid
    from models.judge import Judge
    from models.judge_certificate import JudgeCertificate
    from models.judge_competition import JudgeCompetition
    from models.judge_levels import JudgeLevel, JUDGE_LEVEL_LABELS
    from models.competition import Competition
    from sqlalchemy import select
    async with SessionLocal() as db:
        judge = await db.get(Judge, uuid.UUID(judge_id))
        if not judge:
            return {"error": "Judge not found"}
        certs = await db.execute(
            select(JudgeCertificate).where(JudgeCertificate.judge_id == uuid.UUID(judge_id))
        )
        certificates = certs.scalars().all()
        comps_result = await db.execute(
            select(JudgeCompetition).where(JudgeCompetition.judge_id == uuid.UUID(judge_id))
        )
        comp_assignments = comps_result.scalars().all()
        competitions = []
        for ca in comp_assignments:
            comp = await db.get(Competition, ca.competition_id)
            if comp:
                competitions.append({"competition_name": comp.name, "role": ca.role})
        level_label = JUDGE_LEVEL_LABELS.get(JudgeLevel(judge.level)) if judge.level else None
    return templates.TemplateResponse("judge_profile.html", {
        "request": request,
        "judge": judge,
        "certificates": certificates,
        "competitions": competitions,
        "level_label": level_label,
    })


@app.get("/organizers/{organizer_id}/profile")
async def organizer_profile(organizer_id: str, request: Request):
    import uuid
    from models.organizer import Organizer
    from models.organizer_sponsor import OrganizerSponsor
    from models.competition import Competition
    from sqlalchemy import select
    async with SessionLocal() as db:
        org = await db.get(Organizer, uuid.UUID(organizer_id))
        if not org:
            return {"error": "Organizer not found"}
        sponsors_result = await db.execute(
            select(OrganizerSponsor).where(OrganizerSponsor.organizer_id == uuid.UUID(organizer_id))
            .order_by(OrganizerSponsor.tier)
        )
        sponsors = sponsors_result.scalars().all()
        comps_result = await db.execute(
            select(Competition).where(Competition.organizer_id == uuid.UUID(organizer_id))
            .order_by(Competition.date_start.desc())
        )
        competitions = comps_result.scalars().all()
    return templates.TemplateResponse("organizer_profile.html", {
        "request": request,
        "organizer": org,
        "sponsors": sponsors,
        "competitions": competitions,
    })


@app.get("/judges-list")
async def judges_list(request: Request):
    from sqlalchemy import select
    from models.judge import Judge
    async with SessionLocal() as db:
        result = await db.execute(select(Judge).order_by(Judge.last_name))
        judges = result.scalars().all()
    return templates.TemplateResponse("judges_list.html", {
        "request": request,
        "judges": judges,
    })


@app.get("/organizers-list")
async def organizers_list(request: Request):
    from sqlalchemy import select
    from models.organizer import Organizer
    async with SessionLocal() as db:
        result = await db.execute(select(Organizer).order_by(Organizer.name))
        organizers = result.scalars().all()
    return templates.TemplateResponse("organizers_list.html", {
        "request": request,
        "organizers": organizers,
    })


@app.get("/teams/{team_id}/room")
async def team_room(team_id: str, request: Request):
    from sqlalchemy import select
    from models.team import Team
    from models.team_member import TeamMember
    from models.team_sponsor import TeamSponsor
    from models.athlete import Athlete
    from models.coach import Coach
    from models.match import Match
    import uuid
    tid = uuid.UUID(team_id)
    async with SessionLocal() as db:
        team = await db.get(Team, tid)
        if not team:
            return {"error": "Team not found"}
        members_result = await db.execute(
            select(TeamMember).where(TeamMember.team_id == tid)
        )
        members = members_result.scalars().all()
        for m in members:
            if m.athlete_id:
                m.athlete = await db.get(Athlete, m.athlete_id)
        sponsors_result = await db.execute(
            select(TeamSponsor).where(TeamSponsor.team_id == tid)
        )
        sponsors = sponsors_result.scalars().all()
        coach = await db.get(Coach, team.coach_id) if team.coach_id else None
        matches_result = await db.execute(
            select(Match).where(
                (Match.home_team_id == tid) | (Match.away_team_id == tid)
            ).order_by(Match.round_number, Match.match_date)
        )
        matches = matches_result.scalars().all()
    return templates.TemplateResponse("team_room.html", {
        "request": request,
        "team": team,
        "members": members,
        "sponsors": sponsors,
        "coach": coach,
        "matches": matches,
    })


@app.get("/asl/divisions/{division_id}")
async def asl_division_page(division_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    from models.match_discipline_result import MatchDisciplineResult
    from collections import defaultdict
    import uuid
    did = uuid.UUID(division_id)
    async with SessionLocal() as db:
        division = await db.get(ASLDivision, did)
        if not division:
            return {"error": "Division not found"}
        league = await db.get(ASLLeague, division.league_id)
        standings_result = await db.execute(
            select(TeamStanding)
            .where(TeamStanding.asl_division_id == did)
            .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
        )
        standings = standings_result.scalars().all()
        team_map = {}
        for s in standings:
            t = await db.get(Team, s.team_id)
            s.team = t
            if t:
                team_map[str(s.team_id)] = t
        matches_result = await db.execute(
            select(Match)
            .where(Match.asl_division_id == did)
            .order_by(Match.round_number, Match.match_date)
        )
        matches = matches_result.scalars().all()
        for m in matches:
            for tid in [m.home_team_id, m.away_team_id]:
                if str(tid) not in team_map:
                    t = await db.get(Team, tid)
                    if t:
                        team_map[str(tid)] = t
        matches_by_round = defaultdict(list)
        for m in matches:
            matches_by_round[m.round_number or 1].append(m)
        discipline_results = {}
        for m in matches:
            if m.status == 'completed':
                dr_result = await db.execute(
                    select(MatchDisciplineResult).where(MatchDisciplineResult.match_id == m.id)
                )
                discipline_results[str(m.id)] = dr_result.scalars().all()
        completed_count = sum(1 for m in matches if m.status == 'completed')
        rounds_order = sorted(matches_by_round.keys())
    return templates.TemplateResponse("asl_division.html", {
        "request": request,
        "league": league,
        "division": division,
        "standings": standings,
        "matches": matches,
        "matches_by_round": dict(matches_by_round),
        "rounds_order": rounds_order,
        "team_map": team_map,
        "discipline_results": discipline_results,
        "completed_count": completed_count,
    })


@app.get("/asl/{league_id}")
async def asl_home(league_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.asl_team_division import ASLTeamDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    import uuid
    lid = uuid.UUID(league_id)
    async with SessionLocal() as db:
        league = await db.get(ASLLeague, lid)
        if not league:
            return {"error": "League not found"}
        divs_result = await db.execute(
            select(ASLDivision).where(ASLDivision.league_id == lid).order_by(ASLDivision.name)
        )
        divisions = divs_result.scalars().all()
        standings_by_division = {}
        total_teams = 0
        for div in divisions:
            td_result = await db.execute(
                select(ASLTeamDivision).where(ASLTeamDivision.division_id == div.id)
            )
            total_teams += len(td_result.scalars().all())
            s_result = await db.execute(
                select(TeamStanding)
                .where(TeamStanding.asl_division_id == div.id)
                .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
            )
            standings = s_result.scalars().all()
            for s in standings:
                s.team = await db.get(Team, s.team_id)
            standings_by_division[str(div.id)] = standings
        matches_result = await db.execute(
            select(Match).where(Match.asl_division_id.in_([d.id for d in divisions]))
            .order_by(Match.match_date.desc()).limit(20)
        )
        recent_matches = matches_result.scalars().all()
        team_names = {}
        div_names = {str(d.id): d.name for d in divisions}
        for m in recent_matches:
            for tid in [m.home_team_id, m.away_team_id]:
                if str(tid) not in team_names:
                    t = await db.get(Team, tid)
                    if t:
                        team_names[str(tid)] = t.name
        matches_count_result = await db.execute(
            select(Match).where(Match.asl_division_id.in_([d.id for d in divisions]))
        )
        total_matches = len(matches_count_result.scalars().all())
    return templates.TemplateResponse("asl_home.html", {
        "request": request,
        "league": league,
        "divisions": divisions,
        "standings_by_division": standings_by_division,
        "recent_matches": recent_matches,
        "team_names": team_names,
        "div_names": div_names,
        "total_teams": total_teams,
        "total_matches": total_matches,
    })


@app.get("/asl/{league_id}/final-four")
async def asl_final_four(league_id: str, request: Request):
    from sqlalchemy import select
    from models.asl_league import ASLLeague
    from models.asl_division import ASLDivision
    from models.team_standing import TeamStanding
    from models.team import Team
    from models.match import Match
    import uuid
    lid = uuid.UUID(league_id)
    async with SessionLocal() as db:
        league = await db.get(ASLLeague, lid)
        if not league:
            return {"error": "League not found"}
        divs_result = await db.execute(
            select(ASLDivision).where(ASLDivision.league_id == lid).order_by(ASLDivision.name)
        )
        divisions = divs_result.scalars().all()
        # Лидеры каждого дивизиона
        qualifiers = {}
        for div in divisions:
            s_result = await db.execute(
                select(TeamStanding)
                .where(TeamStanding.asl_division_id == div.id)
                .order_by(TeamStanding.points.desc(), TeamStanding.disciplines_won.desc())
                .limit(1)
            )
            top = s_result.scalar_one_or_none()
            if top:
                qualifiers[str(div.id)] = await db.get(Team, top.team_id)
        # Final Four матчи по типу
        ff_matches = await db.execute(
            select(Match).where(
                Match.asl_division_id == None,
                Match.competition_division_id == None
            )
        )
        # Пока финальные матчи хранятся отдельно — упрощённая версия
        sf1 = sf2 = final = third = None
        sf1_teams = sf2_teams = final_teams = third_teams = []
        champion = None
    return templates.TemplateResponse("asl_final_four.html", {
        "request": request,
        "league": league,
        "divisions": divisions,
        "qualifiers": qualifiers,
        "sf1": sf1, "sf1_teams": sf1_teams,
        "sf2": sf2, "sf2_teams": sf2_teams,
        "final": final, "final_teams": final_teams,
        "third": third, "third_teams": third_teams,
        "champion": champion,
    })




@app.get("/competitions-list")
async def competitions_list(request: Request):
    from sqlalchemy import select
    from models.competition import Competition
    async with SessionLocal() as db:
        result = await db.execute(select(Competition).order_by(Competition.date_start.desc()))
        competitions = result.scalars().all()
    return templates.TemplateResponse("competitions_list.html", {
        "request": request,
        "competitions": competitions,
    })


@app.get("/rankings")
async def rankings_page(request: Request, division: str = "MEN_U80", age_group: str = "SENIOR"):
    import datetime
    from services.ranking_service import RankingService
    from models.weight_category import WeightCategory
    from sqlalchemy import select, and_
    async with SessionLocal() as db:
        svc = RankingService(db)
        ranking = await svc.get_ranking(division, datetime.datetime.utcnow().year)
        result = await db.execute(
            select(WeightCategory)
            .where(and_(WeightCategory.is_active == True, WeightCategory.age_group == age_group))
            .order_by(WeightCategory.sort_order)
        )
        categories = result.scalars().all()
    groups = {"MEN": [], "WOMEN": [], "PARA_MEN": [], "PARA_WOMEN": []}
    for c in categories:
        if c.code.startswith("PARA_WOMEN"):
            groups["PARA_WOMEN"].append((c.code, c.name))
        elif c.code.startswith("PARA_MEN"):
            groups["PARA_MEN"].append((c.code, c.name))
        elif "WOMEN" in c.code:
            groups["WOMEN"].append((c.code, c.name))
        else:
            groups["MEN"].append((c.code, c.name))

    if division.startswith("PARA_WOMEN"):
        active_group = "PARA_WOMEN"
    elif division.startswith("PARA_MEN"):
        active_group = "PARA_MEN"
    elif "WOMEN" in division:
        active_group = "WOMEN"
    else:
        active_group = "MEN"

    age_groups = [("SENIOR", "Senior"), ("JUNIOR", "Junior"), ("YOUTH", "Youth"), ("MASTERS", "Masters 40+")]

    # MASTERS и JUNIOR/YOUTH не имеют PARA категорий
    if age_group in ("MASTERS", "JUNIOR", "YOUTH"):
        available_groups = ["MEN", "WOMEN"]
        if active_group not in available_groups:
            active_group = "MEN"
    else:
        available_groups = ["MEN", "WOMEN", "PARA_MEN", "PARA_WOMEN"]

    active_categories = groups[active_group]
    return templates.TemplateResponse("rankings.html", {
        "request": request,
        "ranking": ranking,
        "active_division": division,
        "active_group": active_group,
        "active_age_group": age_group,
        "active_categories": active_categories,
        "groups": groups,
        "age_groups": age_groups,
        "season_year": datetime.datetime.utcnow().year,
    })


@app.get("/teams-list")
async def teams_list_page(request: Request):
    from models.team import Team
    from sqlalchemy import select
    async with SessionLocal() as db:
        result = await db.execute(select(Team).order_by(Team.name))
        teams = result.scalars().all()
    return templates.TemplateResponse("teams_list.html", {
        "request": request,
        "teams": teams,
    })
