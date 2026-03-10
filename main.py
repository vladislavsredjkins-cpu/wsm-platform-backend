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
    allow_credentials=False,
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




@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("static/logo.jpg")


@app.get("/register/organizer")
async def register_organizer_page(request: Request):
    return templates.TemplateResponse("register_organizer.html", {"request": request})


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


@app.get("/competitions/{competition_id}/page")
async def competition_page(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        # Дивизионы
        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            # Дисциплины
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            # Участники
            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            # Атлеты
            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            # Результаты по дисциплинам
            results_map = {}  # discipline_id -> {participant_id -> result}
            standings_map = {}  # discipline_id -> {participant_id -> standing}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

                st_result = await db.execute(
                    select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
                )
                standings_map[str(disc.id)] = {str(s.participant_id): s for s in st_result.scalars().all()}

            # Overall standings
            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
                .order_by(OverallStanding.overall_place)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            # Порядок старта для каждой дисциплины
            start_orders = {}
            for i, disc in enumerate(disciplines):
                if i == 0:
                    # Первая - по жеребьёвке
                    ordered = sorted(participants, key=lambda p: (p.lot_number or 999, p.bib_no or 999))
                elif disc.is_final:
                    # Финальная - реверс по очкам
                    def get_points(p):
                        o = overall_standings.get(str(p.id))
                        return float(o.total_points) if o else 0
                    ordered = sorted(participants, key=get_points)
                else:
                    # Остальные - реверс по месту в предыдущей
                    prev_disc = disciplines[i-1]
                    def get_prev_place(p):
                        st = standings_map.get(str(prev_disc.id), {}).get(str(p.id))
                        return st.place if st and hasattr(st, 'place') else 999
                    ordered = sorted(participants, key=get_prev_place, reverse=True)
                start_orders[str(disc.id)] = {str(p.id): idx+1 for idx, p in enumerate(ordered)}

            sorted_participants = sorted(
                participants,
                key=lambda p: overall_standings[str(p.id)].overall_place
                    if overall_standings.get(str(p.id)) and overall_standings[str(p.id)].overall_place
                    else 999
            )
            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": sorted_participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "standings_map": standings_map,
                "overall_standings": overall_standings,
                "start_orders": start_orders,
            })

    return templates.TemplateResponse("competition_page.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
    })


# ─── ADMIN PANEL ────────────────────────────────────────────────────────────

@app.get("/competitions/{competition_id}/admin")
async def competition_admin(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            results_map = {}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "overall_standings": overall_standings,
            })

    return templates.TemplateResponse("competition_admin.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
    })


@app.post("/competitions/{competition_id}/admin/save-result")
async def save_result(competition_id: str, request: Request):
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    data = await request.json()
    discipline_id = uuid.UUID(data["discipline_id"])
    participant_id = uuid.UUID(data["participant_id"])
    primary_value = data.get("primary_value")
    secondary_value = data.get("secondary_value")
    reps = data.get("reps")
    status_flag = data.get("status_flag")

    async with SessionLocal() as db:
        existing = await db.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == discipline_id,
                DisciplineResult.participant_id == participant_id
            )
        )
        result = existing.scalar_one_or_none()

        if result:
            if primary_value is not None:
                result.primary_value = primary_value if primary_value != "" else None
            if secondary_value is not None:
                result.secondary_value = secondary_value if secondary_value != "" else None
            if reps is not None:
                result.reps = reps if reps != "" else None
            if status_flag is not None:
                result.status_flag = status_flag if status_flag != "" else None
        else:
            result = DisciplineResult(
                competition_discipline_id=discipline_id,
                participant_id=participant_id,
                primary_value=primary_value if primary_value != "" else None,
                secondary_value=secondary_value if secondary_value != "" else None,
                reps=reps if reps != "" else None,
                status_flag=status_flag if status_flag != "" else None,
            )
            db.add(result)

        await db.commit()
    return {"ok": True}


@app.post("/competitions/{competition_id}/admin/recalculate/{division_id}")
async def recalculate_standings(competition_id: str, division_id: str, request: Request):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select, delete
    import uuid
    from decimal import Decimal

    div_id = uuid.UUID(division_id)

    async with SessionLocal() as db:
        # Дисциплины
        discs_result = await db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == div_id)
            .order_by(CompetitionDiscipline.order_no)
        )
        disciplines = discs_result.scalars().all()

        # Участники
        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == div_id)
        )
        participants = parts_result.scalars().all()
        n = len(participants)

        total_points = {str(p.id): Decimal("0") for p in participants}

        for disc in disciplines:
            # Результаты этой дисциплины
            res_result = await db.execute(
                select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
            )
            results = {str(r.participant_id): r for r in res_result.scalars().all()}

            # Определяем режим сортировки по discipline_mode
            mode = disc.discipline_mode or "AMRAP_REPS"
            reverse = mode in ("AMRAP_REPS", "MAX_WEIGHT_WITHIN_CAP", "AMRAP_DISTANCE")

            def sort_key(p):
                r = results.get(str(p.id))
                if not r:
                    return (-1, 0) if reverse else (999999, 0)
                if r.reps is not None:
                    return (r.reps, 0)
                if r.primary_value is not None:
                    sec = float(r.secondary_value) if r.secondary_value else 0
                    return (float(r.primary_value), sec)
                return (-1, 0) if reverse else (999999, 0)

            sorted_parts = sorted(participants, key=sort_key, reverse=reverse)

            # Удаляем старые standings этой дисциплины
            await db.execute(
                delete(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
            )

            # Записываем новые standings
            place = 1
            for p in sorted_parts:
                r = results.get(str(p.id))
                has_result = r and (r.primary_value is not None or r.reps is not None)
                pts = Decimal(str(n - place + 1)) if has_result else Decimal("0")
                st = DisciplineStanding(
                    competition_discipline_id=disc.id,
                    participant_id=p.id,
                    place=place if has_result else n,
                    points_for_discipline=pts,
                )
                db.add(st)
                if has_result:
                    total_points[str(p.id)] += pts
                    place += 1

        # Overall standings
        await db.execute(
            delete(OverallStanding).where(OverallStanding.competition_division_id == div_id)
        )

        sorted_overall = sorted(participants, key=lambda p: total_points[str(p.id)], reverse=True)
        for i, p in enumerate(sorted_overall):
            o = OverallStanding(
                competition_division_id=div_id,
                participant_id=p.id,
                total_points=total_points[str(p.id)],
                overall_place=i + 1,
            )
            db.add(o)

        await db.commit()

    return {"ok": True, "recalculated": len(participants)}


# ─── REFEREE APP API ─────────────────────────────────────────────────────────

@app.get("/results/discipline/{discipline_id}/sheet")
async def get_discipline_sheet(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        disc = await db.get(CompetitionDiscipline, disc_id)
        if not disc:
            from fastapi import HTTPException
            raise HTTPException(404, "Discipline not found")

        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == disc.competition_division_id)
            .order_by(Participant.lot_number, Participant.bib_no)
        )
        participants = parts_result.scalars().all()

        res_result = await db.execute(
            select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc_id)
        )
        results = {str(r.participant_id): r for r in res_result.scalars().all()}

        sheet = []
        for p in participants:
            ath = await db.get(Athlete, p.athlete_id)
            r = results.get(str(p.id))
            sheet.append({
                "participant_id": str(p.id),
                "bib_no": p.bib_no,
                "lot_number": p.lot_number,
                "first_name": ath.first_name if ath else "",
                "last_name": ath.last_name if ath else "",
                "country": ath.country if ath else "",
                "primary_value": float(r.primary_value) if r and r.primary_value is not None else None,
                "secondary_value": float(r.secondary_value) if r and r.secondary_value is not None else None,
                "reps": r.reps if r else None,
                "status_flag": r.status_flag if r else "OK",
            })

    return sheet


@app.post("/results/discipline/{discipline_id}")
async def upsert_discipline_result(discipline_id: str, request: Request):
    from models.discipline_result import DisciplineResult
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)
    data = await request.json()
    participant_id = uuid.UUID(data["participant_id"])

    async with SessionLocal() as db:
        existing = await db.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == disc_id,
                DisciplineResult.participant_id == participant_id
            )
        )
        result = existing.scalar_one_or_none()

        pv = data.get("primary_value")
        sv = data.get("secondary_value")
        reps = data.get("reps")
        flag = data.get("status_flag", "OK")

        if result:
            result.primary_value = pv
            result.secondary_value = sv
            result.reps = reps
            result.status_flag = flag
        else:
            result = DisciplineResult(
                competition_discipline_id=disc_id,
                participant_id=participant_id,
                primary_value=pv,
                secondary_value=sv,
                reps=reps,
                status_flag=flag,
            )
            db.add(result)

        await db.commit()
    return {"ok": True}


@app.post("/disciplines/{discipline_id}/calculate-standings")
async def calculate_discipline_standings(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select, delete
    import uuid
    from decimal import Decimal

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        disc = await db.get(CompetitionDiscipline, disc_id)
        if not disc:
            from fastapi import HTTPException
            raise HTTPException(404, "Discipline not found")

        parts_result = await db.execute(
            select(Participant).where(Participant.competition_division_id == disc.competition_division_id)
        )
        participants = parts_result.scalars().all()
        n = len(participants)

        res_result = await db.execute(
            select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc_id)
        )
        results = {str(r.participant_id): r for r in res_result.scalars().all()}

        mode = disc.discipline_mode or "AMRAP_REPS"
        reverse = mode in ("AMRAP_REPS", "MAX_WEIGHT_WITHIN_CAP", "AMRAP_DISTANCE")

        def sort_key(p):
            r = results.get(str(p.id))
            if not r or (r.primary_value is None and r.reps is None):
                return (-1, 0) if reverse else (999999, 0)
            if r.reps is not None:
                return (r.reps, 0)
            sec = float(r.secondary_value) if r.secondary_value else 0
            return (float(r.primary_value), sec)

        sorted_parts = sorted(participants, key=sort_key, reverse=reverse)

        await db.execute(
            delete(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc_id)
        )

        place = 1
        for p in sorted_parts:
            r = results.get(str(p.id))
            has_result = r and (r.primary_value is not None or r.reps is not None)
            if r and r.status_flag in ("DNS", "DNF", "DSQ"):
                has_result = False
            pts = Decimal(str(n - place + 1)) if has_result else Decimal("0")
            st = DisciplineStanding(
                competition_discipline_id=disc_id,
                participant_id=p.id,
                place=place if has_result else n,
                points_for_discipline=pts,
            )
            db.add(st)
            if has_result:
                place += 1

        # Пересчёт overall standings для всего дивизиона
        div_id = disc.competition_division_id
        all_discs_result = await db.execute(
            select(CompetitionDiscipline).where(CompetitionDiscipline.competition_division_id == div_id)
        )
        all_discs = all_discs_result.scalars().all()

        total_points = {str(p.id): Decimal("0") for p in participants}
        for d in all_discs:
            st_result = await db.execute(
                select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == d.id)
            )
            for st in st_result.scalars().all():
                if str(st.participant_id) in total_points:
                    total_points[str(st.participant_id)] += st.points_for_discipline

        await db.execute(
            delete(OverallStanding).where(OverallStanding.competition_division_id == div_id)
        )

        sorted_overall = sorted(participants, key=lambda p: total_points[str(p.id)], reverse=True)
        for i, p in enumerate(sorted_overall):
            o = OverallStanding(
                competition_division_id=div_id,
                participant_id=p.id,
                total_points=total_points[str(p.id)],
                overall_place=i + 1,
            )
            db.add(o)

        await db.commit()

    return {"ok": True, "discipline": discipline_id}


@app.get("/results/discipline/{discipline_id}/standings")
async def get_discipline_standings(discipline_id: str):
    from models.discipline_standing import DisciplineStanding
    from sqlalchemy import select
    import uuid

    disc_id = uuid.UUID(discipline_id)

    async with SessionLocal() as db:
        result = await db.execute(
            select(DisciplineStanding)
            .where(DisciplineStanding.competition_discipline_id == disc_id)
            .order_by(DisciplineStanding.place)
        )
        standings = result.scalars().all()

    return [
        {
            "participant_id": str(s.participant_id),
            "place": s.place,
            "points_for_discipline": float(s.points_for_discipline),
        }
        for s in standings
    ]


# ─── REFEREE APP — Division/Discipline endpoints ─────────────────────────────

@app.get("/competition-divisions/{division_id}")
async def get_division(division_id: str):
    from models.competition_division import CompetitionDivision
    from fastapi import HTTPException
    import uuid
    async with SessionLocal() as db:
        div = await db.get(CompetitionDivision, uuid.UUID(division_id))
        if not div:
            raise HTTPException(404, "Division not found")
        return {
            "id": str(div.id),
            "competition_id": str(div.competition_id),
            "division_key": div.division_key,
            "age_group": div.age_group,
            "status": div.status,
        }

@app.get("/competition-divisions/{division_id}/disciplines")
async def get_division_disciplines(division_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from sqlalchemy import select
    import uuid
    async with SessionLocal() as db:
        result = await db.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == uuid.UUID(division_id))
            .order_by(CompetitionDiscipline.order_no)
        )
        discs = result.scalars().all()
        return [
            {
                "id": str(d.id),
                "discipline_name": d.discipline_name,
                "discipline_mode": d.discipline_mode,
                "result_unit": d.result_unit,
                "time_cap_seconds": d.time_cap_seconds,
                "is_final": d.is_final,
                "order_no": d.order_no,
            }
            for d in discs
        ]

@app.get("/competition-disciplines/{discipline_id}")
async def get_discipline(discipline_id: str):
    from models.competition_discipline import CompetitionDiscipline
    from fastapi import HTTPException
    import uuid
    async with SessionLocal() as db:
        d = await db.get(CompetitionDiscipline, uuid.UUID(discipline_id))
        if not d:
            raise HTTPException(404, "Discipline not found")
        return {
            "id": str(d.id),
            "competition_division_id": str(d.competition_division_id),
            "discipline_name": d.discipline_name,
            "discipline_mode": d.discipline_mode,
            "result_unit": d.result_unit,
            "time_cap_seconds": d.time_cap_seconds,
            "is_final": d.is_final,
            "order_no": d.order_no,
        }


# ─── PRINT PROTOCOL ──────────────────────────────────────────────────────────

@app.get("/competitions/{competition_id}/protocol")
async def competition_protocol(competition_id: str, request: Request):
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.competition_discipline import CompetitionDiscipline
    from models.participant import Participant
    from models.athlete import Athlete
    from models.discipline_result import DisciplineResult
    from models.discipline_standing import DisciplineStanding
    from models.overall_standing import OverallStanding
    from sqlalchemy import select
    import uuid

    async with SessionLocal() as db:
        comp = await db.get(Competition, uuid.UUID(competition_id))
        if not comp:
            return templates.TemplateResponse("404.html", {"request": request})

        divs_result = await db.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == uuid.UUID(competition_id))
        )
        divisions = divs_result.scalars().all()

        divisions_data = []
        for div in divisions:
            discs_result = await db.execute(
                select(CompetitionDiscipline)
                .where(CompetitionDiscipline.competition_division_id == div.id)
                .order_by(CompetitionDiscipline.order_no)
            )
            disciplines = discs_result.scalars().all()

            parts_result = await db.execute(
                select(Participant).where(Participant.competition_division_id == div.id)
                .order_by(Participant.lot_number, Participant.bib_no)
            )
            participants = parts_result.scalars().all()

            athlete_map = {}
            for p in participants:
                ath = await db.get(Athlete, p.athlete_id)
                if ath:
                    athlete_map[str(p.id)] = ath

            results_map = {}
            standings_map = {}
            for disc in disciplines:
                res_result = await db.execute(
                    select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
                )
                results_map[str(disc.id)] = {str(r.participant_id): r for r in res_result.scalars().all()}

                st_result = await db.execute(
                    select(DisciplineStanding).where(DisciplineStanding.competition_discipline_id == disc.id)
                )
                standings_map[str(disc.id)] = {str(s.participant_id): s for s in st_result.scalars().all()}

            overall_result = await db.execute(
                select(OverallStanding).where(OverallStanding.competition_division_id == div.id)
                .order_by(OverallStanding.overall_place)
            )
            overall_standings = {str(o.participant_id): o for o in overall_result.scalars().all()}

            sorted_participants = sorted(
                participants,
                key=lambda p: overall_standings[str(p.id)].overall_place
                    if overall_standings.get(str(p.id)) and overall_standings[str(p.id)].overall_place
                    else 999
            )

            # Start orders
            start_orders = {}
            for i, disc in enumerate(disciplines):
                if i == 0:
                    ordered = sorted(participants, key=lambda p: (p.lot_number or 999, p.bib_no or 999))
                elif disc.is_final:
                    def get_points(p):
                        o = overall_standings.get(str(p.id))
                        return float(o.total_points) if o else 0
                    ordered = sorted(participants, key=get_points)
                else:
                    prev_disc = disciplines[i-1]
                    def get_prev_place(p):
                        st = standings_map.get(str(prev_disc.id), {}).get(str(p.id))
                        return st.place if st and hasattr(st, 'place') else 999
                    ordered = sorted(participants, key=get_prev_place, reverse=True)
                start_orders[str(disc.id)] = {str(p.id): idx+1 for idx, p in enumerate(ordered)}

            divisions_data.append({
                "division": div,
                "disciplines": disciplines,
                "participants": sorted_participants,
                "athlete_map": athlete_map,
                "results_map": results_map,
                "standings_map": standings_map,
                "overall_standings": overall_standings,
                "start_orders": start_orders,
            })

        # Организатор
        organizer = None
        if comp.organizer_id:
            from models.organizer import Organizer
            organizer = await db.get(Organizer, comp.organizer_id)

    return templates.TemplateResponse("competition_protocol.html", {
        "request": request,
        "competition": comp,
        "divisions_data": divisions_data,
        "organizer": organizer,
    })


# ─── WSM ADMIN PANEL ─────────────────────────────────────────────────────────

@app.get("/admin/pending-organizers")
async def admin_pending(request: Request):
    return templates.TemplateResponse("admin_pending.html", {"request": request})

@app.get("/admin/api/pending-organizers")
async def api_pending_organizers(request: Request):
    from models.user import User
    from models.organizer import Organizer
    from sqlalchemy import select
    from auth.dependencies import get_current_user
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from auth.security import decode_token
    from jose import JWTError

    # Проверяем токен из заголовка
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        user = await db.get(User, int(user_id))
        if not user or user.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        result = await db.execute(
            select(User, Organizer)
            .join(Organizer, Organizer.user_id == User.id, isouter=True)
            .where(User.role == "PENDING")
        )
        rows = result.all()
        return [
            {
                "user_id": u.id,
                "email": u.email,
                "organizer_id": str(o.id) if o else None,
                "name": o.name if o else "—",
                "type": o.type if o else "—",
                "country": o.country if o else "—",
                "city": o.city if o else "—",
                "phone": o.phone if o else "—",
                "website": o.website if o else "—",
                "photo_url": o.photo_url if o else None,
            }
            for u, o in rows
        ]

@app.post("/admin/api/approve-organizer/{user_id}")
async def api_approve_organizer(user_id: int, request: Request):
    from models.user import User
    from auth.security import decode_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        admin_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        admin = await db.get(User, int(admin_id))
        if not admin or admin.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        user = await db.get(User, user_id)
        if not user:
            from fastapi import HTTPException
            raise HTTPException(404, "User not found")

        user.role = "ORGANIZER"
        await db.commit()
    return {"ok": True, "user_id": user_id, "new_role": "ORGANIZER"}

@app.post("/admin/api/reject-organizer/{user_id}")
async def api_reject_organizer(user_id: int, request: Request):
    from models.user import User
    from auth.security import decode_token

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(403, "Not authorized")
    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        admin_id = payload.get("sub")
    except:
        from fastapi import HTTPException
        raise HTTPException(403, "Invalid token")

    async with SessionLocal() as db:
        admin = await db.get(User, int(admin_id))
        if not admin or admin.role != "WSM_ADMIN":
            from fastapi import HTTPException
            raise HTTPException(403, "WSM_ADMIN role required")

        user = await db.get(User, user_id)
        if not user:
            from fastapi import HTTPException
            raise HTTPException(404, "User not found")

        user.role = "REJECTED"
        await db.commit()
    return {"ok": True, "user_id": user_id, "new_role": "REJECTED"}
