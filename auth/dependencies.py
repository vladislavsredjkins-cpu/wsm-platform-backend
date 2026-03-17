from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.database import get_db
from models.user import User
from auth.security import decode_token
from jose import JWTError

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_current_athlete(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.athlete_id:
        raise HTTPException(status_code=403, detail="User is not linked to an athlete profile")
    from models.athlete import Athlete
    athlete = await db.get(Athlete, current_user.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    return athlete


async def require_organizer(current_user: User = Depends(get_current_user)):
    if current_user.role not in ("ORGANIZER", "ADMIN", "WSM_ADMIN"):
        raise HTTPException(status_code=403, detail="Organizer role required")
    return current_user

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ("ADMIN", "WSM_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user


async def require_referee(current_user: User = Depends(get_current_user)):
    if current_user.role not in ("REFEREE", "ADMIN", "WSM_ADMIN"):
        raise HTTPException(status_code=403, detail="Referee role required")
    return current_user

async def require_federation(current_user: User = Depends(get_current_user)):
    if current_user.role not in ("FEDERATION", "ADMIN", "WSM_ADMIN"):
        raise HTTPException(status_code=403, detail="Federation role required")
    return current_user

