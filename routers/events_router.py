from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.user import User
from auth.security import hash_password, create_access_token
from auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional
import uuid
import datetime
import secrets
from sqlalchemy import text

router = APIRouter()

# ── EVENTS ORGANIZER REGISTRATION (auto-approve) ──────────────────
class RegisterOrganizerRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    country: Optional[str] = None

@router.post("/register/organizer")
async def register_events_organizer(data: RegisterOrganizerRequest, db: AsyncSession = Depends(get_db)):
    from models.organizer import Organizer
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="ORGANIZER",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    org = Organizer(
        user_id=user.id,
        name=data.name or data.email,
        country=data.country,
        is_approved=True,
    )
    db.add(org)
    await db.commit()
    return {"status": "ok", "message": "Organizer registered"}

# ── EVENTS JUDGE INVITES ───────────────────────────────────────────
class JudgeInviteCreate(BaseModel):
    competition_id: str
    email: str
    name: Optional[str] = None

@router.post("/invite-judge")
async def invite_judge(data: JudgeInviteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    token = secrets.token_urlsafe(32)
    await db.execute(text("""
        INSERT INTO events_judge_invites (competition_id, email, name, token)
        VALUES (:comp_id, :email, :name, :token)
    """), {
        "comp_id": data.competition_id,
        "email": data.email,
        "name": data.name,
        "token": token,
    })
    await db.commit()
    invite_url = f"https://events.worldstrongman.org/judge/{token}"
    return {"status": "ok", "token": token, "invite_url": invite_url}

@router.get("/judge-invites/{competition_id}")
async def list_judge_invites(competition_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(text("""
        SELECT * FROM events_judge_invites WHERE competition_id = :comp_id ORDER BY created_at DESC
    """), {"comp_id": competition_id})
    return [dict(r) for r in result.mappings().all()]

@router.get("/judge-access/{token}")
async def judge_access(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT * FROM events_judge_invites WHERE token = :token AND status = 'pending'
    """), {"token": token})
    invite = result.mappings().first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or expired invite")
    await db.execute(text("""
        UPDATE events_judge_invites SET status = 'used', used_at = NOW() WHERE token = :token
    """), {"token": token})
    await db.commit()
    judge_token = create_access_token({
        "sub": str(invite["id"]),
        "role": "REFEREE",
        "competition_id": str(invite["competition_id"]),
        "email": invite["email"],
        "name": invite["name"],
    })
    return {"access_token": judge_token, "competition_id": str(invite["competition_id"])}

# ── EVENTS PARTICIPANTS ────────────────────────────────────────────
class EventsParticipantCreate(BaseModel):
    events_division_id: uuid.UUID
    competition_id: uuid.UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    country: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    bodyweight_kg: Optional[float] = None
    phone: Optional[str] = None

@router.post("/participants")
async def create_events_participant(data: EventsParticipantCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        INSERT INTO events_participants 
        (events_division_id, competition_id, first_name, last_name, email, country, date_of_birth, bodyweight_kg, phone)
        VALUES (:div_id, :comp_id, :first_name, :last_name, :email, :country, :dob, :bw, :phone)
        RETURNING *
    """), {
        "div_id": str(data.events_division_id),
        "comp_id": str(data.competition_id),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "country": data.country,
        "dob": data.date_of_birth,
        "bw": data.bodyweight_kg,
        "phone": data.phone,
    })
    await db.commit()
    return dict(result.mappings().first())

@router.get("/participants/competition/{competition_id}")
async def list_events_participants(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT ep.*, ed.name as division_name 
        FROM events_participants ep
        LEFT JOIN events_divisions ed ON ep.events_division_id = ed.id
        WHERE ep.competition_id = :comp_id
        ORDER BY ed.name, ep.last_name
    """), {"comp_id": str(competition_id)})
    return [dict(r) for r in result.mappings().all()]

@router.get("/participants/division/{events_division_id}")
async def list_events_participants_by_division(events_division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT * FROM events_participants 
        WHERE events_division_id = :div_id
        ORDER BY bib_no, last_name
    """), {"div_id": str(events_division_id)})
    return [dict(r) for r in result.mappings().all()]

@router.patch("/participants/{participant_id}/bib")
async def set_events_participant_bib(participant_id: uuid.UUID, bib_no: int, db: AsyncSession = Depends(get_db)):
    await db.execute(text(
        "UPDATE events_participants SET bib_no = :bib WHERE id = :id"
    ), {"bib": bib_no, "id": str(participant_id)})
    await db.commit()
    return {"status": "ok"}

@router.delete("/participants/{participant_id}")
async def delete_events_participant(participant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await db.execute(text(
        "DELETE FROM events_participants WHERE id = :id"
    ), {"id": str(participant_id)})
    await db.commit()
    return {"status": "ok"}

# ── EVENTS DIVISIONS ───────────────────────────────────────────────
@router.post("/divisions")
async def create_events_division(data: dict, db: AsyncSession = Depends(get_db)):
    await db.execute(text("""
        INSERT INTO events_divisions (id, competition_id, name, gender, weight_min, weight_max, age_group, format, team_size, sport_type)
        VALUES (gen_random_uuid(), :competition_id, :name, :gender, :weight_min, :weight_max, :age_group, :format, :team_size, :sport_type)
    """), {
        "competition_id": data.get("competition_id"),
        "name": data.get("name"),
        "gender": data.get("gender", "male"),
        "weight_min": data.get("weight_min"),
        "weight_max": data.get("weight_max"),
        "age_group": data.get("age_group", "open"),
        "format": data.get("format", "individual"),
        "team_size": data.get("team_size"),
        "sport_type": data.get("sport_type", "strongman"),
    })
    await db.commit()
    return {"status": "ok"}

@router.get("/divisions/{competition_id}")
async def get_events_divisions(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(
        "SELECT * FROM events_divisions WHERE competition_id = :cid ORDER BY order_num"
    ), {"cid": str(competition_id)})
    return [dict(r) for r in result.mappings().all()]

# ── EVENTS DISCIPLINES ─────────────────────────────────────────────
class DisciplineCreate(BaseModel):
    discipline_name: str
    discipline_mode: Optional[str] = None
    order_no: Optional[int] = None
    time_cap_seconds: Optional[int] = None
    implement_weight: Optional[float] = None
    result_unit: Optional[str] = None
    notes: Optional[str] = None

@router.post("/divisions/{events_division_id}/disciplines")
async def create_events_discipline(events_division_id: uuid.UUID, data: DisciplineCreate, db: AsyncSession = Depends(get_db)):
    from models.competition_discipline import CompetitionDiscipline
    discipline = CompetitionDiscipline(
        events_division_id=events_division_id,
        discipline_name=data.discipline_name,
        discipline_mode=data.discipline_mode,
        order_no=data.order_no,
        time_cap_seconds=data.time_cap_seconds,
        implement_weight=data.implement_weight,
        result_unit=data.result_unit,
        notes=data.notes,
    )
    db.add(discipline)
    await db.commit()
    await db.refresh(discipline)
    return discipline

@router.get("/divisions/{events_division_id}/disciplines")
async def list_events_disciplines(events_division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_discipline import CompetitionDiscipline
    result = await db.execute(
        select(CompetitionDiscipline)
        .where(CompetitionDiscipline.events_division_id == events_division_id)
        .order_by(CompetitionDiscipline.order_no)
    )
    return result.scalars().all()

# ── PUBLIC TOURNAMENTS LIST ────────────────────────────────────────
@router.get("/tournaments")
async def list_events_tournaments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT * FROM competitions 
        WHERE is_events = TRUE AND status = 'PUBLISHED'
        ORDER BY date_start ASC
    """))
    return [dict(r) for r in result.mappings().all()]

@router.get("/tournaments/all")
async def list_all_events_tournaments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT * FROM competitions 
        WHERE is_events = TRUE
        ORDER BY date_start ASC
    """))
    return [dict(r) for r in result.mappings().all()]

# ── EVENTS STATS ───────────────────────────────────────────────────
@router.get("/stats")
async def events_stats(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text as sql_text
    tournaments = await db.execute(sql_text("SELECT COUNT(*) FROM competitions WHERE is_events = TRUE"))
    athletes = await db.execute(sql_text("SELECT COUNT(*) FROM events_participants"))
    organizers = await db.execute(sql_text("SELECT COUNT(*) FROM users WHERE role = 'ORGANIZER'"))
    return {
        "tournaments": tournaments.scalar(),
        "athletes": athletes.scalar(),
        "organizers": organizers.scalar(),
    }

# ── ORGANIZER'S EVENTS TOURNAMENTS ────────────────────────────────
@router.get("/my-tournaments")
async def my_events_tournaments(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(text("""
        SELECT c.* FROM competitions c
        JOIN organizers o ON o.id = c.organizer_id
        WHERE c.is_events = TRUE AND o.user_id = :user_id
        ORDER BY c.created_at DESC
    """), {"user_id": str(current_user.id)})
    return [dict(r) for r in result.mappings().all()]
