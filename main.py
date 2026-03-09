from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy as sa
from db.database import SessionLocal

from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import competitions, divisions, athletes, ranking, disciplines, participants, results, auth, judges, organizers, coaches, teams, matches

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
        comps_result = await db.execute(
            select(Competition).where(Competition.organizer_id == uuid.UUID(organizer_id))
            .order_by(Competition.date_start.desc())
        )
        competitions = comps_result.scalars().all()
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
