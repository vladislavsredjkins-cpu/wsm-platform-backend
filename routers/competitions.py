from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition import Competition
from auth.dependencies import require_organizer
from models.user import User
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

router = APIRouter(prefix="/competitions", tags=["competitions"])


class CompetitionCreate(BaseModel):
    name: str
    date_start: Optional[datetime.date] = None
    date_end: Optional[datetime.date] = None
    city: Optional[str] = None
    country: Optional[str] = None
    coefficient_q: float = 1.0
    season_id: Optional[uuid.UUID] = None


class CompetitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    date_start: Optional[datetime.date]
    date_end: Optional[datetime.date]
    city: Optional[str]
    country: Optional[str]
    coefficient_q: float

    class Config:
        from_attributes = True


@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    data: CompetitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer),
):
    competition = Competition(
        id=uuid.uuid4(),
        name=data.name,
        competition_type=getattr(data, "competition_type", None),
        organizer_email=getattr(data, "organizer_email", None),
        status="DRAFT",
        date_start=data.date_start,
        date_end=data.date_end,
        city=data.city,
        country=data.country,
        coefficient_q=data.coefficient_q,
        season_id=data.season_id,
    )
    db.add(competition)
    await db.commit()
    await db.refresh(competition)
    return competition


@router.get("/", response_model=list[CompetitionResponse])
async def list_competitions(db: AsyncSession = Depends(get_db), published_only: bool = False):
    query = select(Competition)
    if published_only:
        query = query.where(Competition.status == 'PUBLISHED')
    result = await db.execute(query.order_by(Competition.date_start.desc()))
    return result.scalars().all()


@router.get("/{competition_id}", response_model=CompetitionResponse)
async def get_competition(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition
@router.post("/{competition_id}/banner")
async def upload_banner(competition_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    from pathlib import Path
    import shutil
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Not found")
    banner_dir = Path("uploads/banners")
    banner_dir.mkdir(parents=True, exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"{competition_id}_banner.{ext}"
    with open(banner_dir / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    competition.banner_url = f"/uploads/banners/{filename}"
    await db.commit()
    return {"banner_url": competition.banner_url}

@router.patch("/{competition_id}")
async def update_competition(competition_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in data.items():
        if hasattr(competition, key):
            setattr(competition, key, value)
    await db.commit()
    return {"status": "ok"}

@router.get("/{competition_id}/sponsors")
async def list_competition_sponsors(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    result = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.competition_id == competition_id))
    return result.scalars().all()

@router.post("/{competition_id}/sponsors")
async def add_competition_sponsor(competition_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    sponsor = CompetitionSponsor(
        competition_id=competition_id,
        name=data.get('name'),
        website_url=data.get('website_url'),
        tier=data.get('tier', 'FREE')
    )
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    return sponsor

@router.delete("/{competition_id}/sponsors/{sponsor_id}")
async def delete_competition_sponsor(competition_id: uuid.UUID, sponsor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    result = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.id == sponsor_id))
    sponsor = result.scalar_one_or_none()
    if sponsor:
        await db.delete(sponsor)
        await db.commit()
    return {"status": "ok"}

@router.get("/{competition_id}/sponsors")
async def list_competition_sponsors(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    result = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.competition_id == competition_id))
    return result.scalars().all()

@router.post("/{competition_id}/sponsors")
async def add_competition_sponsor(competition_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    sponsor = CompetitionSponsor(
        competition_id=competition_id,
        name=data.get('name'),
        website_url=data.get('website_url'),
        tier=data.get('tier', 'FREE')
    )
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    return sponsor

@router.delete("/{competition_id}/sponsors/{sponsor_id}")
async def delete_competition_sponsor(competition_id: uuid.UUID, sponsor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    result = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.id == sponsor_id))
    sponsor = result.scalar_one_or_none()
    if sponsor:
        await db.delete(sponsor)
        await db.commit()
    return {"status": "ok"}

@router.post("/{competition_id}/sponsors/{sponsor_id}/logo")
async def upload_sponsor_logo(competition_id: uuid.UUID, sponsor_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    from models.competition_sponsor import CompetitionSponsor
    from pathlib import Path
    import shutil
    result = await db.execute(select(CompetitionSponsor).where(CompetitionSponsor.id == sponsor_id))
    sponsor = result.scalar_one_or_none()
    if not sponsor:
        raise HTTPException(status_code=404, detail="Not found")
    logo_dir = Path("uploads/sponsors")
    logo_dir.mkdir(parents=True, exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"comp_{sponsor_id}.{ext}"
    with open(logo_dir / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    sponsor.logo_url = f"/uploads/sponsors/{filename}"
    await db.commit()
    return {"logo_url": sponsor.logo_url}
