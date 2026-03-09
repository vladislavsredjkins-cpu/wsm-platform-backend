import uuid, os, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from db.database import get_db
from models.team import Team
from models.team_member import TeamMember
from models.team_sponsor import TeamSponsor
from auth.dependencies import get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])

class TeamCreate(BaseModel):
    name: str
    country: Optional[str] = None
    email: Optional[str] = None
    competition_division_id: Optional[uuid.UUID] = None
    coach_id: Optional[uuid.UUID] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    email: Optional[str] = None
    competition_division_id: Optional[uuid.UUID] = None
    coach_id: Optional[uuid.UUID] = None
    status: Optional[str] = None

class MemberCreate(BaseModel):
    athlete_id: uuid.UUID
    role: str = "ATHLETE_1"  # ATHLETE_1 / ATHLETE_2 / RESERVE
    bodyweight_kg: Optional[float] = None

class SponsorCreate(BaseModel):
    name: str
    website_url: Optional[str] = None
    tier: str = "STANDARD"  # GENERAL / STANDARD

@router.get("/")
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).order_by(Team.name))
    return result.scalars().all()

@router.get("/{team_id}")
async def get_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/")
async def create_team(data: TeamCreate, db: AsyncSession = Depends(get_db),
                      current_user=Depends(get_current_user)):
    team = Team(**data.dict(), status="pending")
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team

@router.patch("/{team_id}")
async def update_team(team_id: uuid.UUID, data: TeamUpdate,
                      db: AsyncSession = Depends(get_db),
                      current_user=Depends(get_current_user)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for k, v in data.dict(exclude_none=True).items():
        setattr(team, k, v)
    await db.commit()
    await db.refresh(team)
    return team

@router.post("/{team_id}/logo")
async def upload_logo(team_id: uuid.UUID, file: UploadFile = File(...),
                      db: AsyncSession = Depends(get_db),
                      current_user=Depends(get_current_user)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    os.makedirs("uploads/teams", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"uploads/teams/{team_id}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    team.logo_url = f"/{filename}"
    await db.commit()
    return {"logo_url": team.logo_url}

# --- Members ---
@router.get("/{team_id}/members")
async def list_members(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    return result.scalars().all()

@router.post("/{team_id}/members")
async def add_member(team_id: uuid.UUID, data: MemberCreate,
                     db: AsyncSession = Depends(get_db),
                     current_user=Depends(get_current_user)):
    # Проверяем лимиты: макс 2 атлета + 1 запасной
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    members = result.scalars().all()
    role_counts = {}
    for m in members:
        role_counts[m.role] = role_counts.get(m.role, 0) + 1
    if data.role in ("ATHLETE_1", "ATHLETE_2") and role_counts.get(data.role, 0) >= 1:
        raise HTTPException(status_code=400, detail=f"Role {data.role} already taken")
    if data.role == "RESERVE" and role_counts.get("RESERVE", 0) >= 1:
        raise HTTPException(status_code=400, detail="Reserve spot already taken")
    member = TeamMember(team_id=team_id, **data.dict())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member

@router.delete("/{team_id}/members/{member_id}")
async def remove_member(team_id: uuid.UUID, member_id: uuid.UUID,
                        db: AsyncSession = Depends(get_db),
                        current_user=Depends(get_current_user)):
    member = await db.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(member)
    await db.commit()
    return {"status": "removed"}

# --- Sponsors ---
@router.get("/{team_id}/sponsors")
async def list_sponsors(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamSponsor).where(TeamSponsor.team_id == team_id)
    )
    return result.scalars().all()

@router.post("/{team_id}/sponsors")
async def add_sponsor(team_id: uuid.UUID, data: SponsorCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user=Depends(get_current_user)):
    result = await db.execute(
        select(TeamSponsor).where(TeamSponsor.team_id == team_id)
    )
    sponsors = result.scalars().all()
    generals = [s for s in sponsors if s.tier == "GENERAL"]
    standards = [s for s in sponsors if s.tier == "STANDARD"]
    if data.tier == "GENERAL" and len(generals) >= 1:
        raise HTTPException(status_code=400, detail="Only 1 general sponsor allowed")
    if data.tier == "STANDARD" and len(standards) >= 2:
        raise HTTPException(status_code=400, detail="Only 2 standard sponsors allowed")
    sponsor = TeamSponsor(team_id=team_id, **data.dict())
    db.add(sponsor)
    await db.commit()
    await db.refresh(sponsor)
    return sponsor

@router.post("/{team_id}/sponsors/{sponsor_id}/logo")
async def upload_sponsor_logo(team_id: uuid.UUID, sponsor_id: uuid.UUID,
                               file: UploadFile = File(...),
                               db: AsyncSession = Depends(get_db),
                               current_user=Depends(get_current_user)):
    sponsor = await db.get(TeamSponsor, sponsor_id)
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    os.makedirs("uploads/team_sponsors", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"uploads/team_sponsors/{sponsor_id}.{ext}"
    with open(filename, "wb") as f:
        shutil.copyfileobj(file.file, f)
    sponsor.logo_url = f"/{filename}"
    await db.commit()
    return {"logo_url": sponsor.logo_url}

@router.delete("/{team_id}/sponsors/{sponsor_id}")
async def remove_sponsor(team_id: uuid.UUID, sponsor_id: uuid.UUID,
                         db: AsyncSession = Depends(get_db),
                         current_user=Depends(get_current_user)):
    sponsor = await db.get(TeamSponsor, sponsor_id)
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    await db.delete(sponsor)
    await db.commit()
    return {"status": "removed"}
