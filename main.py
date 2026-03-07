from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select, func
import sqlalchemy as sa
from datetime import date, datetime
from uuid import UUID
from typing import Literal

from db.database import SessionLocal

from models.athlete import Athlete
from models.competition import Competition
from models.result import Result
from models.competition_division import CompetitionDivision
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.discipline_result import DisciplineResult
from models.ranking_point import RankingPoint
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.ranking_snapshot import RankingSnapshot
from models.season import Season
from models.competition_class import CompetitionClass
from models.protest import Protest

from api.athletes import router as athletes_router
from api.competitions import router as competitions_router
from api.divisions import router as divisions_router
from api.disciplines import router as disciplines_router
from api.participants import router as participants_router
from api.discipline_results import router as discipline_results_router
from api.standings import router as standings_router
from api.ranking import router as ranking_router
from api.protests import router as protests_router


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
    approved_at: datetime | None = None
    live_at: datetime | None = None
    locked_at: datetime | None = None

    class Config:
        from_attributes = True


class DisciplineCreate(BaseModel):
    order_no: int = Field(..., ge=1, le=50)
    discipline_name: str
    discipline_mode: DisciplineMode
    time_cap_seconds: int | None = Field(None, ge=1, le=3600)
    lanes_per_heat: int | None = Field(None, ge=1, le=20)
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

class FinalizeOut(BaseModel):
    competition_id: UUID
    season_year: int
    rows_written: int


class RankingItem(BaseModel):
    athlete_id: UUID
    first_name: str
    last_name: str
    country: str
    points: float


class RankingOut(BaseModel):
    division: DivisionKey
    format: CompetitionFormat
    season_year: int
    limit: int
    offset: int
    items: list[RankingItem]

class RankingSnapshotOut(BaseModel):
    snapshot_created: int

class DisciplineStandingRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    place: int
    points_for_discipline: float

class DisciplineStandingOut(BaseModel):
    competition_discipline_id: UUID
    items: list[DisciplineStandingRow]


class OverallStandingRow(BaseModel):
    participant_id: UUID
    athlete_id: UUID
    bib_no: int | None = None
    total_points: float
    place: int
    tie_break_value: float | None = None

class OverallStandingOut(BaseModel):
    division_id: UUID
    items: list[OverallStandingRow]

ProtestStatus = Literal["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]


class ProtestCreate(BaseModel):
    competition_id: UUID
    athlete_id: UUID
    reason: str = Field(..., min_length=3, max_length=2000)


class ProtestReview(BaseModel):
    status: ProtestStatus


class ProtestOut(BaseModel):
    id: UUID
    competition_id: UUID
    athlete_id: UUID
    reason: str
    status: ProtestStatus
    created_at: datetime | None = None

    class Config:
        from_attributes = True

# =========================
# App
# =========================

app = FastAPI(title="World Strongman Platform API", version="1.0.0")


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

app.include_router(athletes_router)
app.include_router(competitions_router)
app.include_router(divisions_router)
app.include_router(disciplines_router)
app.include_router(participants_router)
app.include_router(discipline_results_router)
app.include_router(standings_router)
app.include_router(ranking_router)
app.include_router(protests_router)

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
    return {"service": "wsm-platform-backend", "build": "RANKING_V1_CORE_06_FINALIZE_FIX"}

@app.get("/db-test")
async def db_test():
    async with SessionLocal() as session:
        result = await session.execute(sa.text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}


@app.post("/divisions/{division_id}/calculate-standings", response_model=OverallStandingOut)
async def calculate_standings(division_id: UUID):
    async with SessionLocal() as session:
        # 1) division
        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status in ("RESULTS_VALIDATED", "LOCKED"):
            raise HTTPException(
                status_code=400,
                detail="Standings are already validated or locked",
            )
        # 2) participants
        p_res = await session.execute(
            select(Participant).where(Participant.competition_division_id == division_id)
        )
        participants = list(p_res.scalars().all())
        if not participants:
            return OverallStandingOut(division_id=division_id, items=[])

        participant_ids = [p.id for p in participants]
        p_map = {p.id: p for p in participants}

        # 3) disciplines
        d_res = await session.execute(
            select(CompetitionDiscipline)
            .where(CompetitionDiscipline.competition_division_id == division_id)
            .order_by(CompetitionDiscipline.order_no.asc())
        )
        disciplines = list(d_res.scalars().all())

        # clear old standings for this division
        await session.execute(
            sa.delete(DisciplineStanding).where(
                DisciplineStanding.competition_discipline_id.in_(
                    select(CompetitionDiscipline.id).where(
                        CompetitionDiscipline.competition_division_id == division_id
                    )
                )
            )
        )

        await session.execute(
            sa.delete(OverallStanding).where(
                OverallStanding.competition_division_id == division_id
            )
        )

        points_map: dict[UUID, float] = {pid: 0.0 for pid in participant_ids}

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

        # 4) discipline standings
        for disc in disciplines:
            r_res = await session.execute(
                select(DisciplineResult).where(
                    DisciplineResult.competition_discipline_id == disc.id,
                    DisciplineResult.participant_id.in_(participant_ids),
                )
            )
            results = list(r_res.scalars().all())
            results_by_pid = {r.participant_id: r for r in results}

            rows = []
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
                    rows.append(
                        {
                            "participant_id": pid,
                            "status_flag": "DNS",
                            "primary_value": None,
                            "secondary_value": None,
                        }
                    )

            rows_sorted = sorted(rows, key=lambda x: sort_key_for_mode(disc.discipline_mode, x))

            n = len(rows_sorted)
            for idx, row in enumerate(rows_sorted, start=1):
                pid = row["participant_id"]
                pts = float(n - idx + 1)
                points_map[pid] += pts

                session.add(
                    DisciplineStanding(
                        competition_discipline_id=disc.id,
                        participant_id=pid,
                        place=idx,
                        points_for_discipline=pts,
                    )
                )

        # 5) overall standings
        overall_rows = []
        for pid in participant_ids:
            tie_break_value = None
            overall_rows.append(
                {
                    "participant_id": pid,
                    "total_points": float(points_map[pid]),
                    "tie_break_value": tie_break_value,
                }
            )

        # higher total_points better, then lighter bodyweight better
        overall_rows_sorted = sorted(
            overall_rows,
            key=lambda x: (
                -x["total_points"],
                str(x["participant_id"]),
            ),
        )
        items_out = []
        for place_no, row in enumerate(overall_rows_sorted, start=1):
            pid = row["participant_id"]
            p = p_map[pid]

            session.add(
                OverallStanding(
                    competition_division_id=division_id,
                    participant_id=pid,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

            items_out.append(
                OverallStandingRow(
                    participant_id=pid,
                    athlete_id=p.athlete_id,
                    bib_no=p.bib_no,
                    total_points=row["total_points"],
                    place=place_no,
                    tie_break_value=row["tie_break_value"],
                )
            )

        await session.commit()

        return OverallStandingOut(
            division_id=division_id,
            items=items_out,
        )

@app.post("/divisions/{division_id}/results/validate", response_model=OverallStandingOut)
async def validate_division_results(division_id: UUID):
    async with SessionLocal() as session:

        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        standings = await calculate_standings(division_id)

        div.status = "RESULTS_VALIDATED"

        await session.commit()

        return standings

@app.post("/divisions/{division_id}/lock")
async def lock_division(division_id: UUID):
    async with SessionLocal() as session:

        div = await session.get(CompetitionDivision, division_id)
        if not div:
            raise HTTPException(status_code=404, detail="Division not found")

        if div.status != "RESULTS_VALIDATED":
            raise HTTPException(
                status_code=400,
                detail="Division must be RESULTS_VALIDATED before lock",
            )

        div.status = "LOCKED"
        div.locked_at = datetime.utcnow()

        await session.commit()

        return {
            "division_id": division_id,
            "status": "LOCKED",
        }



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

