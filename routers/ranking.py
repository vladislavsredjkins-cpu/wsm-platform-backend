from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from services.ranking_service import RankingService
import datetime

router = APIRouter(prefix="/ranking", tags=["ranking"])


@router.get("/{division_key}")
async def get_ranking(division_key: str, db: AsyncSession = Depends(get_db)):
    service = RankingService(db)
    season_year = datetime.datetime.utcnow().year
    ranking = await service.get_ranking(division_key, season_year)
    return {
        "division_key": division_key,
        "season_year": season_year,
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "athletes": ranking,
    }