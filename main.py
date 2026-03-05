from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from datetime import date
from uuid import UUID

from db.database import engine, SessionLocal
from db.base import Base
from models.athlete import Athlete
from models.competition import Competition
from models.result import Result
from models.competition_division import CompetitionDivision
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.discipline_result import DisciplineResult

class AthleteCreate(BaseModel):
    first_name: str
    last_name: str
    country: str


class AthleteOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    country: str

    class Config:
        from_attributes = True

class CompetitionCreate(BaseModel):
    name: str
    date_start: date
    date_end: date | None = None
    city: str | None = None
    country: str | None = None
    coefficient_q: float = Field(1.0, ge=0.1, le=10.0)


class CompetitionOut(CompetitionCreate):
    id: UUID

    class Config:
        from_attributes = True

from typing import Literal

DivisionKey = Literal["MEN", "WOMEN", "PARA"]
CompetitionFormat = Literal["CLASSIC", "PARA", "RELAY", "TEAM_BATTLE"]
LifecycleStatus = Literal["DRAFT", "SUBMITTED", "APPROVED", "LIVE", "RESULTS_VALIDATED", "LOCKED"]

DisciplineMode = Literal[
    "TIME_WITH_DISTANCE_FALLBACK",
    "AMRAP_REPS",
    "AMRAP_DISTANCE",
    "MAX_WEIGHT_WITHIN_CAP",
    "RELAY_DUAL_METRIC",
]

class DivisionCreate(BaseModel):
    division_key: DivisionKey
    format: CompetitionFormat
    status: LifecycleStatus = "DRAFT"

class DivisionOut(DivisionCreate):
    id: UUID
    competition_id: UUID

    class Config:
        from_attributes = True


class DisciplineCreate(BaseModel):
    order_no: int = Field(..., ge=1, le=50)
    discipline_name: str
    discipline_mode: DisciplineMode
    time_cap_seconds: int | None = Field(None, ge=1, le=3600)
    lanes_per_heat: int | None = Field(None, ge=1, le=4)
    track_length_meters: int | None = Field(None, ge=1, le=10000)

class DisciplineOut(DisciplineCreate):
    id: UUID
    competition_division_id: UUID

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    athlete_id: UUID
    bib_no: int | None = Field(None, ge=1, le=9999)
    bodyweight_kg: float | None = Field(None, ge=0.0, le=400.0)

class ParticipantOut(ParticipantCreate):
    id: UUID
    competition_division_id: UUID

    class Config:
        from_attributes = True

class ResultCreate(BaseModel):
    competition_id: UUID
    athlete_id: UUID
    place: int = Field(..., ge=1, le=500)
    status: str = "approved"


class ResultOut(ResultCreate):
    id: UUID

    class Config:
        from_attributes = True



app = FastAPI(title="World Strongman Platform API", version="1.0.0")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vladislavredjkins-cpu.github.io",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/__build")
def __build():
    return {"service": "wsm-platform-backend", "build": "RANKING_V1_CORE_01"}


@app.get("/ranking")
def get_ranking(
    division: str = Query("MEN"),
    format: str = Query("CLASSIC"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return {
        "division": division,
        "format": format,
        "limit": limit,
        "offset": offset,
        "items": [],
    }


@app.get("/athletes", response_model=list[AthleteOut])
async def get_athletes():
    async with SessionLocal() as session:
        result = await session.execute(select(Athlete))
        return result.scalars().all()


@app.post("/athletes", response_model=AthleteOut)
async def create_athlete(payload: AthleteCreate):
    async with SessionLocal() as session:
        athlete = Athlete(**payload.model_dump())
        session.add(athlete)
        await session.commit()
        await session.refresh(athlete)
        return athlete

@app.post("/competitions", response_model=CompetitionOut)
async def create_competition(payload: CompetitionCreate):
    async with SessionLocal() as session:
        c = Competition(**payload.model_dump())
        session.add(c)
        await session.commit()
        await session.refresh(c)
        return c


@app.get("/competitions", response_model=list[CompetitionOut])
async def list_competitions():
    async with SessionLocal() as session:
        res = await session.execute(
            select(Competition).order_by(Competition.date_start.desc())
        )
        return list(res.scalars().all())

@app.post("/competitions/{competition_id}/divisions", response_model=DivisionOut)
async def create_division(competition_id: UUID, payload: DivisionCreate):
    async with SessionLocal() as session:
        d = CompetitionDivision(
            competition_id=competition_id,
            division_key=payload.division_key,
            format=payload.format,
            status=payload.status,
        )
        session.add(d)
        await session.commit()
        await session.refresh(d)
        return d


@app.get("/competitions/{competition_id}/divisions", response_model=list[DivisionOut])
async def list_divisions(competition_id: UUID):
    async with SessionLocal() as session:
        res = await session.execute(
            select(CompetitionDivision).where(CompetitionDivision.competition_id == competition_id)
        )
        return list(res.scalars().all())

@app.post("/divisions/{division_id}/disciplines", response_model=DisciplineOut)
async def create_discipline(division_id: UUID, payload: DisciplineCreate):
    async with SessionLocal() as session:
        disc = CompetitionDiscipline(
            competition_division_id=division_id,
            order_no=payload.order_no,
            discipline_name=payload.discipline_name,
            discipline_mode=payload.discipline_mode,
            time_cap_seconds=payload.time_cap_seconds,
            lanes_per_heat=payload.lanes_per_heat,
            track_length_meters=payload.track_length_meters,
        )
        session.add(disc)
        await session.commit()
        await session.refresh(disc)
        return disc


@app.get("/divisions/{division_id}/disciplines", response_model=list[DisciplineOut])
async def list_disciplines(division_id: UUID):
    async with SessionLocal() as session:
        res = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        return list(res.scalars().all())

@app.post("/divisions/{division_id}/participants", response_model=ParticipantOut)
async def create_participant(division_id: UUID, payload: ParticipantCreate):
    async with SessionLocal() as session:
        p = Participant(
            competition_division_id=division_id,
            athlete_id=payload.athlete_id,
            bib_no=payload.bib_no,
            bodyweight_kg=payload.bodyweight_kg,
        )
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p


@app.get("/divisions/{division_id}/participants", response_model=list[ParticipantOut])
async def list_participants(division_id: UUID):
    async with SessionLocal() as session:
        res = await session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        return list(res.scalars().all())

@app.post("/results", response_model=ResultOut)
async def create_result(payload: ResultCreate):
    async with SessionLocal() as session:
        r = Result(**payload.model_dump())
        session.add(r)
        await session.commit()
        await session.refresh(r)
        return r


@app.get("/results", response_model=list[ResultOut])
async def list_results(competition_id: UUID | None = None):
    async with SessionLocal() as session:
        stmt = select(Result)

        if competition_id:
            stmt = stmt.where(Result.competition_id == competition_id)

        res = await session.execute(stmt.order_by(Result.place.asc()))

        return list(res.scalars().all())
