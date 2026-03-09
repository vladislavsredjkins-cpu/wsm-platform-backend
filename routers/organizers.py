from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.organizer import Organizer
from models.organizer_sponsor import OrganizerSponsor
from auth.dependencies import get_current_user
from models.user import User
from pydantic import BaseModel
from typing import Optional
import uuid, shutil, datetime
from pathlib import Path
from decimal import Decimal

router = APIRouter(prefix="/organizers", tags=["organizers"])

UPLOAD_DIR = Path("uploads/organizers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SPONSOR_TIERS = ["BRONZE", "SILVER", "GOLD", "TITLE"]

class OrganizerCreate(BaseModel):
    type: str = "person"  # federation / club / person
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    instagram: Optional[str] = None

class OrganizerResponse(BaseModel):
    id: uuid.UUID
    type: str
    name: str
    country: Optional[str]
    city: Optional[str]
    photo_url: Optional[str]
    website: Optional[str]
    email: Optional[str]

    class Config:
        from_attributes = True

class SponsorCreate(BaseModel):
    name: str
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    tier: str = "BRONZE"
    paid_until: Optional[datetime.date] = None
    price_paid: Optional[Decimal] = None

class SponsorResponse(BaseModel):
    id: uuid.UUID
    organizer_id: uuid.UUID
    name: str
    logo_url: Optional[str]
    website_url: Optional[str]
    tier: str
    paid_until: Optional[datetime.date]
    price_paid: Optional[Decimal]

    class Config:
        from_attributes = True


@router.get("/", response_model=list[OrganizerResponse])
async def list_organizers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organizer).order_by(Organizer.name))
    return result.scalars().all()


@router.get("/{organizer_id}", response_model=OrganizerResponse)
async def get_organizer(organizer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    org = await db.get(Organizer, organizer_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return org


@router.post("/", response_model=OrganizerResponse)
async def create_organizer(
    data: OrganizerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    org = Organizer(id=uuid.uuid4(), user_id=current_user.id, **data.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.patch("/{organizer_id}", response_model=OrganizerResponse)
async def update_organizer(
    organizer_id: uuid.UUID,
    data: OrganizerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    org = await db.get(Organizer, organizer_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    if org.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    await db.commit()
    await db.refresh(org)
    return org


@router.post("/{organizer_id}/photo")
async def upload_photo(
    organizer_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    org = await db.get(Organizer, organizer_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    if org.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    filename = f"{organizer_id}.{ext}"
    with open(UPLOAD_DIR / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    org.photo_url = f"/uploads/organizers/{filename}"
    await db.commit()
    return {"photo_url": org.photo_url}


@router.get("/{organizer_id}/sponsors", response_model=list[SponsorResponse])
async def get_sponsors(organizer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OrganizerSponsor).where(OrganizerSponsor.organizer_id == organizer_id)
        .order_by(OrganizerSponsor.tier)
    )
    return result.scalars().all()


@router.post("/{organizer_id}/sponsors", response_model=SponsorResponse)
async def add_sponsor(
    organizer_id: uuid.UUID,
    data: SponsorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    org = await db.get(Organizer, organizer_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    if org.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")
    if data.tier not in SPONSOR_TIERS:
        raise HTTPException(status_code=400, detail=f"Tier must be one of: {SPONSOR_TIERS}")

    sponsor = OrganizerSponsor(id=uuid.uuid4(), organizer_id=organizer_id, **data.model_dump())
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    return sponsor


@router.post("/{organizer_id}/sponsors/{sponsor_id}/logo")
async def upload_sponsor_logo(
    organizer_id: uuid.UUID,
    sponsor_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sponsor = await db.get(OrganizerSponsor, sponsor_id)
    if not sponsor or sponsor.organizer_id != organizer_id:
        raise HTTPException(status_code=404, detail="Sponsor not found")

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Only jpg/png/webp allowed")

    logo_dir = Path("uploads/organizer_sponsors")
    logo_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{sponsor_id}.{ext}"
    with open(logo_dir / filename, "wb") as f:
        shutil.copyfileobj(file.file, f)

    sponsor.logo_url = f"/uploads/organizer_sponsors/{filename}"
    await db.commit()
    return {"logo_url": sponsor.logo_url}


@router.delete("/{organizer_id}/sponsors/{sponsor_id}")
async def remove_sponsor(
    organizer_id: uuid.UUID,
    sponsor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sponsor = await db.get(OrganizerSponsor, sponsor_id)
    if not sponsor or sponsor.organizer_id != organizer_id:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    await db.delete(sponsor)
    await db.commit()
    return {"status": "ok"}
