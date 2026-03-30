from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.user import User
from models.athlete import Athlete
from auth.security import hash_password, verify_password, create_access_token
from auth.dependencies import get_current_user
from pydantic import BaseModel
import datetime
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str
    athlete_id: str | None = None
    judge_id: str | None = None
    organizer_id: str | None = None
    team_id: str | None = None

class LinkAthleteRequest(BaseModel):
    athlete_id: uuid.UUID

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=user.id, email=user.email, role=user.role)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=token, user_id=user.id,
        email=user.email, role=user.role,
        athlete_id=str(user.athlete_id) if user.athlete_id else None,
        judge_id=str(user.judge_id) if user.judge_id else None,
        organizer_id=str(user.organizer_id) if user.organizer_id else None,
        team_id=str(user.team_id) if hasattr(user, 'team_id') and user.team_id else None,
    )

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "athlete_id": str(current_user.athlete_id) if current_user.athlete_id else None,
        "judge_id": str(current_user.judge_id) if current_user.judge_id else None,
        "organizer_id": str(current_user.organizer_id) if current_user.organizer_id else None,
        "team_id": str(current_user.team_id) if hasattr(current_user, 'team_id') and current_user.team_id else None,
        "is_active": current_user.is_active,
    }

@router.post("/link-athlete")
async def link_athlete(
    data: LinkAthleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    athlete = await db.get(Athlete, data.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    current_user.athlete_id = data.athlete_id
    await db.commit()
    return {"status": "ok", "athlete_id": str(data.athlete_id)}


class LinkJudgeRequest(BaseModel):
    judge_id: uuid.UUID

class LinkOrganizerRequest(BaseModel):
    organizer_id: uuid.UUID

@router.post("/link-judge")
async def link_judge(
    data: LinkJudgeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from models.judge import Judge
    judge = await db.get(Judge, data.judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")
    current_user.judge_id = data.judge_id
    await db.commit()
    return {"status": "ok", "judge_id": str(data.judge_id)}


@router.post("/link-organizer")
async def link_organizer(
    data: LinkOrganizerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from models.organizer import Organizer
    org = await db.get(Organizer, data.organizer_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organizer not found")
    current_user.organizer_id = data.organizer_id
    await db.commit()
    return {"status": "ok", "organizer_id": str(data.organizer_id)}


class RegisterOrganizerRequest(BaseModel):
    # User
    email: str
    password: str
    # Organizer profile
    name: str
    type: str = "person"  # person / club / federation
    country: str | None = None
    city: str | None = None
    website: str | None = None
    phone: str | None = None
    instagram: str | None = None

@router.post("/register/organizer")
async def register_organizer(data: RegisterOrganizerRequest, db: AsyncSession = Depends(get_db)):
    from models.organizer import Organizer

    # Проверяем email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаём User с ролью PENDING
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role="ORGANIZER",
        is_active=True,
    )
    db.add(user)
    await db.flush()  # получаем user.id

    # Создаём Organizer профиль
    org = Organizer(
        user_id=user.id,
        name=data.name,
        type=data.type,
        country=data.country,
        city=data.city,
        email=data.email,
        website=data.website,
        phone=data.phone,
        instagram=data.instagram,
    )
    db.add(org)
    await db.flush()

    # Привязываем organizer к user
    user.organizer_id = org.id
    await db.commit()
    await db.refresh(user)

    return {
        "status": "pending",
        "message": "Registration submitted. Your account is pending approval by WSM Admin.",
        "email": user.email,
        "organizer_id": str(org.id),
    }


# ── EVENTS ORGANIZER REGISTRATION (auto-approve) ─────────────────
@router.post("/register/events-organizer")
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
        name=data.name,
        type=data.type or "club",
        country=data.country,
        email=data.email,
    )
    db.add(org)
    await db.flush()
    user.organizer_id = org.id
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role, "organizer_id": str(org.id)})
    return {"access_token": token, "email": user.email, "role": user.role, "organizer_id": str(org.id)}

# ── ATHLETE REGISTRATION ──────────────────────────────────────────
class RegisterAthleteRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    country: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    bodyweight_kg: float | None = None
    phone: str | None = None
    instagram: str | None = None

@router.post("/register/athlete")
async def register_athlete(data: RegisterAthleteRequest, db: AsyncSession = Depends(get_db)):
    import datetime
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role="ATHLETE", is_active=True)
    db.add(user)
    await db.flush()
    dob = None
    if data.date_of_birth:
        try: dob = datetime.date.fromisoformat(data.date_of_birth)
        except: pass
    athlete = Athlete(
        first_name=data.first_name, last_name=data.last_name,
        country=data.country, gender=data.gender, date_of_birth=dob,
        bodyweight_kg=data.bodyweight_kg, phone=data.phone,
        instagram=data.instagram, email=data.email,
    )
    db.add(athlete)
    await db.flush()
    user.athlete_id = athlete.id
    await db.commit()
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"status": "ok", "athlete_id": str(athlete.id), "access_token": token}


# ── JUDGE REGISTRATION ────────────────────────────────────────────
class RegisterJudgeRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    country: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    instagram: str | None = None
    level: str | None = None

@router.post("/register/judge")
async def register_judge(data: RegisterJudgeRequest, db: AsyncSession = Depends(get_db)):
    from models.judge import Judge
    import datetime
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role="JUDGE", is_active=True)
    db.add(user)
    await db.flush()
    dob = None
    if data.date_of_birth:
        try: dob = datetime.date.fromisoformat(data.date_of_birth)
        except: pass
    judge = Judge(
        user_id=user.id, first_name=data.first_name, last_name=data.last_name,
        country=data.country, gender=data.gender, date_of_birth=dob,
        phone=data.phone, instagram=data.instagram, email=data.email, level=data.level,
    )
    db.add(judge)
    await db.flush()
    user.judge_id = judge.id
    await db.commit()
    return {"status": "pending", "judge_id": str(judge.id), "message": "Application submitted. Pending WSM Admin review."}


# ── COACH REGISTRATION ────────────────────────────────────────────
class RegisterCoachRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    country: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    phone: str | None = None
    instagram: str | None = None
    level: str | None = None

@router.post("/register/coach")
async def register_coach(data: RegisterCoachRequest, db: AsyncSession = Depends(get_db)):
    from models.coach import Coach
    import datetime
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role="COACH", is_active=True)
    db.add(user)
    await db.flush()
    dob = None
    if data.date_of_birth:
        try: dob = datetime.date.fromisoformat(data.date_of_birth)
        except: pass
    coach = Coach(
        user_id=user.id, first_name=data.first_name, last_name=data.last_name,
        country=data.country, gender=data.gender, date_of_birth=dob,
        phone=data.phone, instagram=data.instagram, email=data.email, level=data.level,
    )
    db.add(coach)
    await db.flush()
    user.coach_id = coach.id
    await db.commit()
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"status": "ok", "coach_id": str(coach.id), "access_token": token}


# ── TEAM REGISTRATION ─────────────────────────────────────────────
class RegisterTeamRequest(BaseModel):
    email: str
    password: str
    name: str
    country: str | None = None
    team_email: str | None = None
    athlete1_id: str | None = None
    athlete2_id: str | None = None
    reserve_id: str | None = None
    coach_id: str | None = None

@router.post("/register/team")
async def register_team(data: RegisterTeamRequest, db: AsyncSession = Depends(get_db)):
    from models.team import Team
    from models.team_member import TeamMember
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role="TEAM", is_active=True)
    db.add(user)
    await db.flush()
    team = Team(
        name=data.name, country=data.country,
        email=data.team_email or data.email,
        coach_id=uuid.UUID(data.coach_id) if data.coach_id else None,
        status="pending",
    )
    db.add(team)
    await db.flush()
    # Добавляем членов команды
    roles = [("ATHLETE_1", data.athlete1_id), ("ATHLETE_2", data.athlete2_id), ("RESERVE", data.reserve_id)]
    for role, aid in roles:
        if aid:
            db.add(TeamMember(team_id=team.id, athlete_id=uuid.UUID(aid), role=role))
    user.team_id = team.id
    await db.commit()
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"status": "ok", "team_id": str(team.id), "access_token": token}

from pydantic import BaseModel as PydanticBase

class ChangePasswordRequest(PydanticBase):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"status": "ok", "message": "Password changed successfully"}
