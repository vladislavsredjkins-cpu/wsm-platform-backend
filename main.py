from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy as sa
from db.database import SessionLocal

from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import competitions, divisions, athletes, ranking, disciplines, participants, results, auth

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
