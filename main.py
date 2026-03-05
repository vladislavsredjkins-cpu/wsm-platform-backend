from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from datetime import date
from uuid import UUID
from typing import Literal

from db.database import engine, SessionLocal
from db.base import Base

from models.athlete import Athlete
from models.competition import Competition
from models.result import Result
from models.competition_division import CompetitionDivision
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.discipline_result import DisciplineResult


# =========================
# Pydantic Schemas
# =========================

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


StatusFlag = Literal["OK", "DNF", "DQ", "DNS"]


class DisciplineResultCreate(BaseModel):
    athlete_id: UUID
    primary_value: float | None = None
    secondary_value: float | None = None
    status_flag: StatusFlag = "OK"


class DisciplineResultOut(DisciplineResultCreate):
    id: UUID
    competition_discipline_id: UUID
    participant_id: UUID

    class Config:
        from_attributes = True

class DisciplineLeaderboardRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    place: int
    primary_value: float | None = None
    secondary_value: float | None = None
    status_flag: StatusFlag

class DisciplineLeaderboardOut(BaseModel):
    competition_discipline_id: UUID
    discipline_mode: DisciplineMode
    items: list[DisciplineLeaderboardRow]

class DivisionOverallRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    total_points: float
    place: int

class DivisionOverallOut(BaseModel):
    division_id: UUID
    items: list[DivisionOverallRow]

class ResultCreate(BaseModel):
    competition_id: UUID
    athlete_id: UUID
    place: int = Field(..., ge=1, le=500)
    status: str = "approved"


class ResultOut(ResultCreate):
    id: UUID

    class Config:
        from_attributes = True


# =========================
# App
# =========================

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
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Basic endpoints
# =========================

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/__build")
def __build():
    return {"service": "wsm-platform-backend", "build": "RANKING_V1_CORE_03_LEADERBOARD"}


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


# =========================
# Athletes
# =========================

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


# =========================
# Competitions
# =========================

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


# =========================
# Divisions
# =========================

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
            select(CompetitionDivision).where(
                CompetitionDivision.competition_id == competition_id
            )
        )
        return list(res.scalars().all())


# =========================
# Disciplines
# =========================

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


# =========================
# Participants
# =========================

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
            select(Participant).where(
                Participant.competition_division_id == division_id
            )
        )
        return list(res.scalars().all())


# =========================
# Discipline Results
# =========================

@app.post("/disciplines/{competition_discipline_id}/results", response_model=DisciplineResultOut)
async def upsert_discipline_result(
    competition_discipline_id: UUID, payload: DisciplineResultCreate
):
    async with SessionLocal() as session:

        disc_res = await session.execute(
            select(CompetitionDiscipline).where(
                CompetitionDiscipline.id == competition_discipline_id
            )
        )
        discipline = disc_res.scalar_one_or_none()

        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        part_res = await session.execute(
            select(Participant).where(
                Participant.competition_division_id == discipline.competition_division_id,
                Participant.athlete_id == payload.athlete_id,
            )
        )
        participant = part_res.scalar_one_or_none()

        if not participant:
            raise HTTPException(status_code=404, detail="Participant not found")

                existing_res = await session.execute(
            select(DisciplineResult).where(
                DisciplineResult.competition_discipline_id == competition_discipline_id,
                DisciplineResult.participant_id == participant.id,
            )
        )
        existing = existing_res.scalar_one_or_none()

        if existing:
            existing.primary_value = payload.primary_value
            existing.secondary_value = payload.secondary_value
            existing.status_flag = payload.status_flag
            obj = existing
        else:
            obj = DisciplineResult(
                competition_discipline_id=competition_discipline_id,
                participant_id=participant.id,
                primary_value=payload.primary_value,
                secondary_value=payload.secondary_value,
                status_flag=payload.status_flag,
            )
            session.add(obj)

        await session.commit()
        await session.refresh(obj)

        return obj

@app.get(
    "/disciplines/{competition_discipline_id}/leaderboard",
    response_model=DisciplineLeaderboardOut,
)
async def discipline_leaderboard(competition_discipline_id: UUID):
    async with SessionLocal() as session:
        disc_res = await session.execute(
            select(CompetitionDiscipline).where(CompetitionDiscipline.id == competition_discipline_id)
        )
        discipline = disc_res.scalar_one_or_none()
        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        # load results
        res = await session.execute(
            select(DisciplineResult).where(DisciplineResult.competition_discipline_id == competition_discipline_id)
        )
        results = list(res.scalars().all())

        # build rows with athlete_id + bib
        rows = []
        for r in results:
            p = await session.get(Participant, r.participant_id)
            rows.append(
                {
                    "participant_id": r.participant_id,
                    "athlete_id": p.athlete_id,
                    "bib_no": p.bib_no,
                    "primary_value": float(r.primary_value) if r.primary_value is not None else None,
                    "secondary_value": float(r.secondary_value) if r.secondary_value is not None else None,
                    "status_flag": r.status_flag,
                }
            )

        mode = discipline.discipline_mode

        def sort_key(item: dict):
            # statuses: OK first, then DNS/DNF/DQ at the end
            status = item["status_flag"]
            status_rank = 0 if status == "OK" else 1

            pv = item["primary_value"]
            sv = item["secondary_value"]

            # default missing values go last
            pv_missing = pv is None
            sv_missing = sv is None

            if mode == "TIME_WITH_DISTANCE_FALLBACK":
                # smaller time is better; if time missing, use distance (bigger better)
                # sort by: status, has_time, time asc, has_distance, distance desc
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    pv if pv is not None else 10**12,
                    0 if not sv_missing else 1,
                    -(sv if sv is not None else -1),
                )

            if mode in ("AMRAP_REPS", "AMRAP_DISTANCE", "MAX_WEIGHT_WITHIN_CAP"):
                # bigger primary is better
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                )

            if mode == "RELAY_DUAL_METRIC":
                # dual metric: bigger primary better; then smaller secondary better
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                    0 if not sv_missing else 1,
                    sv if sv is not None else 10**12,
                )

            # fallback: status then primary desc
            return (
                status_rank,
                0 if not pv_missing else 1,
                -(pv if pv is not None else -1),
            )

        rows_sorted = sorted(rows, key=sort_key)

        # assign places (simple 1..N, no ties handling yet)
        items_out: list[DisciplineLeaderboardRow] = []
        for idx, row in enumerate(rows_sorted, start=1):
            items_out.append(
                DisciplineLeaderboardRow(
                    participant_id=row["participant_id"],
                    athlete_id=row["athlete_id"],
                    bib_no=row["bib_no"],
                    place=idx,
                    primary_value=row["primary_value"],
                    secondary_value=row["secondary_value"],
                    status_flag=row["status_flag"],
                )
            )

        return DisciplineLeaderboardOut(
            competition_discipline_id=competition_discipline_id,
            discipline_mode=mode,
            items=items_out,
        )

@app.get("/divisions/{division_id}/leaderboard", response_model=DivisionOverallOut)
async def division_leaderboard(division_id: UUID):
    async with SessionLocal() as session:
        # 1) division exists
        div_res = await session.execute(
            select(CompetitionDivision).where(CompetitionDivision.id == division_id)
        )
        division = div_res.scalar_one_or_none()
        if not division:
            raise HTTPException(status_code=404, detail="Division not found")

        # 2) participants in division
        p_res = await session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(p_res.scalars().all())
        participant_ids = [p.id for p in participants]

        # nothing to compute
        if not participant_ids:
            return DivisionOverallOut(division_id=division_id, items=[])

        # map participant -> athlete/bib
        p_map = {p.id: p for p in participants}

        # 3) disciplines in division
        d_res = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(d_res.scalars().all())

        # points accumulator (higher is better)
        points: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}

        # helper: compute discipline order (place) from discipline_results
        def sort_key_for_mode(mode: str, item: dict):
            status = item["status_flag"]
            status_rank = 0 if status == "OK" else 1

            pv = item["primary_value"]
            sv = item["secondary_value"]

            pv_missing = pv is None
            sv_missing = sv is None

            if mode == "TIME_WITH_DISTANCE_FALLBACK":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    pv if pv is not None else 10**12,
                    0 if not sv_missing else 1,
                    -(sv if sv is not None else -1),
                )

            if mode in ("AMRAP_REPS", "AMRAP_DISTANCE", "MAX_WEIGHT_WITHIN_CAP"):
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                )

            if mode == "RELAY_DUAL_METRIC":
                return (
                    status_rank,
                    0 if not pv_missing else 1,
                    -(pv if pv is not None else -1),
                    0 if not sv_missing else 1,
                    sv if sv is not None else 10**12,
                )

            return (
                status_rank,
                0 if not pv_missing else 1,
                -(pv if pv is not None else -1),
            )

        # 4) for each discipline compute places and assign points
        for disc in disciplines:
            r_res = await session.execute(
                select(DisciplineResult).where(
                    DisciplineResult.competition_discipline_id == disc.id,
                    DisciplineResult.participant_id.in_(participant_ids),
                )
            )
            results = list(r_res.scalars().all())

            # build rows per participant (include missing as DNS-like -> goes last)
            rows = []
            results_by_pid = {r.participant_id: r for r in results}

            for pid in participant_ids:
                r = results_by_pid.get(pid)
                if r:
                    rows.append(
                        {
                            "participant_id": pid,
                            "status_flag": r.status_flag,
                            "primary_value": float(r.primary_value) if r.primary_value is not None else None,
                            "secondary_value": float(r.secondary_value) if r.secondary_value is not None else None,
                        }
                    )
                else:
                    # no result submitted -> treat as DNS for sorting/points
                    rows.append(
                        {
                            "participant_id": pid,
                            "status_flag": "DNS",
                            "primary_value": None,
                            "secondary_value": None,
                        }
                    )

            rows_sorted = sorted(rows, key=lambda x: sort_key_for_mode(disc.discipline_mode, x))

            # points scheme (LIVE): N participants -> first gets N, last gets 1
            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                pid = row["participant_id"]
                pts = float(n - idx + 1)
                points[pid] += pts

        # 5) overall sort (higher total points better)
        overall = sorted(points.items(), key=lambda kv: (-kv[1], str(kv[0])))

        items: list[DivisionOverallRow] = []
        for place_no, (pid, total) in enumerate(overall, start=1):
            p = p_map[pid]
            items.append(
                DivisionOverallRow(
                    participant_id=pid,
                    athlete_id=p.athlete_id,
                    bib_no=p.bib_no,
                    total_points=total,
                    place=place_no,
                )
            )

        return DivisionOverallOut(division_id=division_id, items=items)

# =========================
# Legacy results
# =========================

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
