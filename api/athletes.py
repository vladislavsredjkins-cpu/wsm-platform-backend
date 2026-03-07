from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from db.database import SessionLocal
from models.athlete import Athlete


router = APIRouter(prefix="/athletes", tags=["athletes"])


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


@router.get("", response_model=list[AthleteOut])
async def get_athletes():
    async with SessionLocal() as session:
        result = await session.execute(select(Athlete))
        return result.scalars().all()


@router.post("", response_model=AthleteOut)
async def create_athlete(payload: AthleteCreate):
    async with SessionLocal() as session:
        athlete = Athlete(**payload.model_dump())
        session.add(athlete)
        await session.commit()
        await session.refresh(athlete)
        return athlete
