from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import SessionLocal
from models.athlete import Athlete


router = APIRouter(prefix="/athletes", tags=["athletes"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("")
async def list_athletes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Athlete))
    athletes = result.scalars().all()
    return athletes


@router.post("")
async def create_athlete(athlete: dict, db: AsyncSession = Depends(get_db)):
    new_athlete = Athlete(**athlete)
    db.add(new_athlete)
    await db.commit()
    await db.refresh(new_athlete)
    return new_athlete
