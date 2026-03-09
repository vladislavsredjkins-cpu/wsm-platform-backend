from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy as sa
from db.database import SessionLocal

from routers import competitions, divisions, athletes, ranking, disciplines, participants, results, auth

app = FastAPI(title="World Strongman Platform API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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