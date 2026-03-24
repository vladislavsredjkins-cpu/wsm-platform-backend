from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.competition import Competition
from auth.dependencies import require_organizer, get_current_user_optional
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
    entry_fee_enabled: bool = False
    entry_fee: Optional[float] = None
    registration_deadline: Optional[datetime.date] = None
    entry_fee_non_refundable: bool = True


class CompetitionResponse(BaseModel):
    id: uuid.UUID
    name: str
    date_start: Optional[datetime.date]
    date_end: Optional[datetime.date]
    city: Optional[str]
    country: Optional[str]
    coefficient_q: float
    banner_url: Optional[str] = None
    status: Optional[str] = None
    organizer_email: Optional[str] = None
    competition_type: Optional[str] = None
    description: Optional[str] = None
    organizer_mc_text: Optional[str] = None
    entry_fee_enabled: Optional[bool] = False
    entry_fee: Optional[float] = None
    registration_deadline: Optional[datetime.date] = None
    entry_fee_non_refundable: Optional[bool] = True

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
        organizer_id=current_user.organizer_id if current_user.organizer_id else None,
        entry_fee_enabled=data.entry_fee_enabled,
        entry_fee=data.entry_fee,
        registration_deadline=data.registration_deadline,
        entry_fee_non_refundable=data.entry_fee_non_refundable,
    )
    db.add(competition)
    await db.commit()
    await db.refresh(competition)
    return competition


@router.get("/", response_model=list[CompetitionResponse])
async def list_competitions(
    db: AsyncSession = Depends(get_db),
    published_only: bool = False,
    organizer_id: Optional[str] = None,
    current_user: User = Depends(get_current_user_optional),
):
    query = select(Competition)
    if published_only:
        query = query.where(Competition.status == 'PUBLISHED')
    elif organizer_id:
        import uuid as _uuid
        query = query.where(Competition.organizer_id == _uuid.UUID(organizer_id))
    elif current_user and current_user.role == 'ORGANIZER' and current_user.organizer_id:
        query = query.where(Competition.organizer_id == current_user.organizer_id)
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
    import sys
    sys.path.insert(0, '/var/www/wsm-platform')
    from utils.r2 import upload_file_to_r2
    import os
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Not found")
    ext = file.filename.split(".")[-1]
    filename = f"banners/{competition_id}_banner.{ext}"
    file_bytes = await file.read()
    upload_file_to_r2(file_bytes, filename, file.content_type or "image/jpeg")
    public_url = os.getenv("R2_PUBLIC_URL", "")
    competition.banner_url = f"{public_url}/uploads/{filename}"
    db.add(competition)
    await db.flush()
    await db.commit()
    await db.refresh(competition)
    return {"banner_url": competition.banner_url}

@router.patch("/{competition_id}")
async def update_competition(competition_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Competition).where(Competition.id == competition_id))
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Not found")
    date_fields = ["date_start", "date_end", "registration_deadline"]
    float_fields = ["entry_fee", "coefficient_q"]
    for key, value in data.items():
        if hasattr(competition, key):
            if key in date_fields and isinstance(value, str) and value:
                import datetime as dt
                value = dt.date.fromisoformat(value)
            elif key in float_fields and isinstance(value, str) and value:
                value = float(value)
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
    ext = file.filename.split(".")[-1]
    filename = f"comp_{sponsor_id}.{ext}"
    file_bytes = await file.read()
    from utils.r2 import upload_file_to_r2
    upload_file_to_r2(file_bytes, filename, file.content_type or "image/jpeg")
    sponsor.logo_url = f"https://pub-22fdd3117dc246539752f3a04b02035f.r2.dev/uploads/{filename}"
    await db.commit()
    return {"logo_url": sponsor.logo_url}


# ── JUDGE ASSIGNMENTS ─────────────────────────────────────────
@router.get("/{competition_id}/judges")
async def get_competition_judges(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.judge_competition import JudgeCompetition
    from models.judge import Judge
    from sqlalchemy import select
    result = await db.execute(
        select(JudgeCompetition, Judge)
        .join(Judge, JudgeCompetition.judge_id == Judge.id)
        .where(JudgeCompetition.competition_id == competition_id)
    )
    rows = result.all()
    return [
        {
            "id": str(jc.id),
            "judge_id": str(jc.judge_id),
            "role": jc.role,
            "first_name": j.first_name,
            "last_name": j.last_name,
            "country": j.country,
            "license_number": j.level,
        }
        for jc, j in rows
    ]

@router.post("/{competition_id}/judges")
async def assign_judge(competition_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    from models.judge_competition import JudgeCompetition
    from sqlalchemy import select
    # проверяем дубликат
    existing = await db.execute(
        select(JudgeCompetition).where(
            JudgeCompetition.competition_id == competition_id,
            JudgeCompetition.judge_id == uuid.UUID(data["judge_id"])
        )
    )
    if existing.scalar():
        raise HTTPException(400, "Judge already assigned")
    jc = JudgeCompetition(
        competition_id=competition_id,
        judge_id=uuid.UUID(data["judge_id"]),
        role=data.get("role", "Judge")
    )
    db.add(jc)
    await db.commit()
    await db.refresh(jc)
    return {"id": str(jc.id), "judge_id": str(jc.judge_id), "role": jc.role}

@router.delete("/{competition_id}/judges/{assignment_id}")
async def remove_judge(competition_id: uuid.UUID, assignment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.judge_competition import JudgeCompetition
    jc = await db.get(JudgeCompetition, assignment_id)
    if not jc or jc.competition_id != competition_id:
        raise HTTPException(404)
    await db.delete(jc)
    await db.commit()
    return {"ok": True}

# ── DRAW / LOTTERY ─────────────────────────────────────────────
@router.post("/{competition_id}/divisions/{division_id}/draw")
async def auto_draw(competition_id: uuid.UUID, division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Авто-жеребьёвка: случайный порядок для дисциплины 1"""
    from models.participant import Participant
    from sqlalchemy import select
    import random

    result = await db.execute(
        select(Participant).where(Participant.competition_division_id == division_id)
    )
    participants = result.scalars().all()
    if not participants:
        raise HTTPException(404, "No participants in this division")

    # Перемешиваем случайно
    indices = list(range(1, len(participants) + 1))
    random.shuffle(indices)

    for p, lot in zip(participants, indices):
        p.lot_number = lot
        db.add(p)

    await db.flush()
    await db.commit()

    return [{"participant_id": str(p.id), "lot_number": p.lot_number} for p in sorted(participants, key=lambda x: x.lot_number)]

@router.post("/{competition_id}/divisions/{division_id}/draw/reverse")
async def reverse_draw(competition_id: uuid.UUID, division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Реверсная жеребьёвка для дисциплины 2+: кто хуже — стартует первым"""
    from models.participant import Participant
    from models.overall_standing import OverallStanding
    from sqlalchemy import select

    result = await db.execute(
        select(Participant).where(Participant.competition_division_id == division_id)
    )
    participants = result.scalars().all()
    if not participants:
        raise HTTPException(404, "No participants")

    # Берём текущие standings
    standings_result = await db.execute(
        select(OverallStanding).where(OverallStanding.competition_division_id == division_id)
    )
    standings = {s.participant_id: s.place for s in standings_result.scalars().all()}

    # Сортируем: у кого place больше (хуже) — lot меньше (стартует первым)
    sorted_participants = sorted(
        participants,
        key=lambda p: -(standings.get(p.id, 999))
    )

    for lot, p in enumerate(sorted_participants, 1):
        p.lot_number = lot
        db.add(p)

    await db.flush()
    await db.commit()

    return [{"participant_id": str(p.id), "lot_number": p.lot_number} for p in sorted(participants, key=lambda x: x.lot_number)]

@router.patch("/{competition_id}/divisions/{division_id}/draw")
async def update_lot(competition_id: uuid.UUID, division_id: uuid.UUID, data: dict, db: AsyncSession = Depends(get_db)):
    """Ручная правка lot номеров"""
    from models.participant import Participant
    # data = {"lots": [{"participant_id": "...", "lot_number": 1}, ...]}
    for item in data.get("lots", []):
        p = await db.get(Participant, uuid.UUID(item["participant_id"]))
        if p and p.competition_division_id == division_id:
            p.lot_number = item["lot_number"]
            db.add(p)
    await db.flush()
    await db.commit()
    return {"ok": True}

@router.get("/{competition_id}/divisions/{division_id}/participants")
async def get_division_participants(competition_id: uuid.UUID, division_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.participant import Participant
    from models.athlete import Athlete
    from sqlalchemy import select
    result = await db.execute(
        select(Participant, Athlete)
        .join(Athlete, Participant.athlete_id == Athlete.id)
        .where(Participant.competition_division_id == division_id)
        .order_by(Participant.lot_number.nullslast(), Participant.bib_no)
    )
    return [
        {
            "participant_id": str(p.id),
            "athlete_id": str(a.id),
            "first_name": a.first_name,
            "last_name": a.last_name,
            "country": a.country,
            "bib_no": p.bib_no,
            "lot_number": p.lot_number,
        }
        for p, a in result.all()
    ]

# ── LIVE START ORDER API ────────────────────────────────────────
@router.get("/{competition_id}/live-data")
async def get_live_data(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Данные для live-screen и warmup-screen"""
    from models.competition import Competition
    from models.competition_division import CompetitionDivision
    from models.participant import Participant
    from models.athlete import Athlete
    from models.competition_discipline import CompetitionDiscipline as Discipline
    from models.discipline_result import DisciplineResult  # noqa
    from sqlalchemy import select

    comp = await db.get(Competition, competition_id)
    if not comp:
        raise HTTPException(404)

    divs_result = await db.execute(
        select(CompetitionDivision).where(CompetitionDivision.competition_id == competition_id)
    )
    divisions = divs_result.scalars().all()

    result = []
    for div in divisions:
        # Атлеты
        parts_result = await db.execute(
            select(Participant, Athlete)
            .join(Athlete, Participant.athlete_id == Athlete.id)
            .where(Participant.competition_division_id == div.id)
            .order_by(Participant.lot_number.nullslast(), Participant.bib_no)
        )
        participants = [
            {"participant_id": str(p.id), "first_name": a.first_name, "last_name": a.last_name,
             "country": a.country, "bib_no": p.bib_no, "lot_number": p.lot_number}
            for p, a in parts_result.all()
        ]

        # Дисциплины
        discs_result = await db.execute(
            select(Discipline).where(Discipline.competition_division_id == div.id).order_by(Discipline.order_no.nullslast())
        )
        disciplines = discs_result.scalars().all()

        discs_data = []
        for disc in disciplines:
            # Результаты
            res_result = await db.execute(
                select(DisciplineResult).where(DisciplineResult.competition_discipline_id == disc.id)
            )
            results = {str(r.participant_id): str(r.primary_value or "") for r in res_result.scalars().all()}

            # Стартовый порядок для этой дисциплины
            ordered = sorted(participants, key=lambda p: (p["lot_number"] or 999, p["bib_no"] or 999))
            start_order = {p["participant_id"]: idx+1 for idx, p in enumerate(ordered)}

            discs_data.append({
                "id": str(disc.id),
                "name": disc.discipline_name,
                "order_index": disc.order_no,
                "start_order": start_order,
                "results": results,
            })

        result.append({
            "division_id": str(div.id),
            "division_name": str(div.division_key),
            "participants": participants,
            "disciplines": discs_data,
        })

    return {
        "competition_id": str(competition_id),
        "competition_name": comp.name,
        "status": comp.status,
        "divisions": result,
    }

@router.get("/{competition_id}/registrations")
async def list_competition_registrations(competition_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.competition_registration import CompetitionRegistration
    from models.athlete import Athlete
    result = await db.execute(
        select(CompetitionRegistration, Athlete)
        .join(Athlete, CompetitionRegistration.athlete_id == Athlete.id)
        .where(CompetitionRegistration.competition_id == competition_id)
        .order_by(CompetitionRegistration.created_at.desc())
    )
    rows = result.all()
    return [{
        "id": str(r.CompetitionRegistration.id),
        "athlete_email": r.CompetitionRegistration.athlete_email,
        "athlete_name": f"{r.Athlete.first_name} {r.Athlete.last_name}",
        "country": r.Athlete.country,
        "amount_eur": r.CompetitionRegistration.amount_eur,
        "payment_method": r.CompetitionRegistration.payment_method,
        "status": r.CompetitionRegistration.status,
        "paid_at": str(r.CompetitionRegistration.paid_at) if r.CompetitionRegistration.paid_at else None,
        "coupon_code": r.CompetitionRegistration.coupon_code,
        "created_at": str(r.CompetitionRegistration.created_at)
    } for r in rows]
