from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError
from db.database import get_db
from auth.security import decode_token
from models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    return user


def require_roles(*roles: str):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {list(roles)}. Your role: {current_user.role}"
            )
        return current_user
    return checker


# Готовые зависимости для использования в роутерах
require_admin = require_roles("WSM_ADMIN")
require_federation = require_roles("WSM_ADMIN", "FEDERATION_ADMIN")
require_organizer = require_roles("WSM_ADMIN", "FEDERATION_ADMIN", "ORGANIZER")
require_referee = require_roles("WSM_ADMIN", "FEDERATION_ADMIN", "ORGANIZER", "REFEREE")