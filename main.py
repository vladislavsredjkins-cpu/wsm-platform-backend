from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from db.database import engine, SessionLocal
from db.base import Base
from models.athlete import Athlete

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
    return {"service": "wsm-platform-backend", "build": "RANKING_V1"}


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


@app.get("/athletes")
async def get_athletes():
    async with SessionLocal() as session:
        result = await session.execute(select(Athlete))
        return result.scalars().all()
