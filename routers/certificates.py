import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/certificates", tags=["certificates"])

LMS_SECRET = "WSM_LMS_SECRET_2026"

class CertificateWebhook(BaseModel):
    certificate_number: str
    judge_email: str
    course_name: str
    programme_code: Optional[str] = None
    issue_date: Optional[str] = None
    valid_until: Optional[str] = None
    verify_hash: Optional[str] = None
    secret: Optional[str] = None

@router.post("/webhook")
async def receive_certificate(data: CertificateWebhook, db: AsyncSession = Depends(get_db)):
    from models.judge_certificate import JudgeCertificate
    from models.user import User

    if data.secret != LMS_SECRET:
        raise HTTPException(403, "Invalid secret")

    result = await db.execute(select(User).where(User.email == data.judge_email))
    user = result.scalar_one_or_none()
    if not user or not user.judge_id:
        raise HTTPException(404, f"Judge not found: {data.judge_email}")

    # Проверяем дубликат
    existing = await db.execute(
        select(JudgeCertificate).where(JudgeCertificate.certificate_number == data.certificate_number)
    )
    if existing.scalar_one_or_none():
        return {"status": "already_exists"}

    verify_url = f"https://lms.worldstrongman.org/lms/verify/{data.verify_hash}/" if data.verify_hash else None

    issue_date = None
    valid_until = None
    try:
        if data.issue_date:
            issue_date = datetime.date.fromisoformat(data.issue_date)
        if data.valid_until:
            valid_until = datetime.date.fromisoformat(data.valid_until)
    except:
        pass

    cert = JudgeCertificate(
        id=uuid.uuid4(),
        judge_id=user.judge_id,
        title=data.course_name,
        course_name=data.course_name,
        certificate_number=data.certificate_number,
        programme_code=data.programme_code,
        issued_date=issue_date,
        expires_date=valid_until,
        verify_url=verify_url,
        verify_hash=data.verify_hash,
        status='active',
    )
    db.add(cert)
    await db.commit()

    return {"status": "ok", "certificate_number": data.certificate_number}

@router.get("/judge/{judge_id}")
async def get_judge_certificates(judge_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from models.judge_certificate import JudgeCertificate

    result = await db.execute(
        select(JudgeCertificate).where(JudgeCertificate.judge_id == judge_id)
        .order_by(JudgeCertificate.issued_date.desc())
    )
    certs = result.scalars().all()

    output = []
    for c in certs:
        status = c.status or 'active'
        if c.expires_date and c.expires_date < datetime.date.today():
            status = 'expired'
        output.append({
            "id": str(c.id),
            "certificate_number": c.certificate_number,
            "course_name": c.course_name or c.title,
            "programme_code": c.programme_code,
            "issue_date": str(c.issued_date) if c.issued_date else None,
            "valid_until": str(c.expires_date) if c.expires_date else None,
            "verify_url": c.verify_url,
            "status": status,
        })
    return output
