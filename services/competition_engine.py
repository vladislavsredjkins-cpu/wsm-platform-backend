from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


class CompetitionEngine:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_division_standings(self, competition_division_id: UUID):
        """
        Calculate overall standings for a division.
        Logic will be moved here from api/standings.py
        """
        pass
