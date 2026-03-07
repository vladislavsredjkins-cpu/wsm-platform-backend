from logging.config import fileConfig
import os

from sqlalchemy import create_engine
from alembic import context

from db.base import Base

from models.athlete import Athlete
from models.competition import Competition
from models.competition_division import CompetitionDivision
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.protest import Protest
from models.ranking_point import RankingPoint
from models.ranking_snapshot import RankingSnapshot
from models.result import Result
from models.season import Season
from models.weight_category import WeightCategory
from models.team_rule import TeamRule

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set")

sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

print("DB_URL =", db_url)
print("SYNC_DB_URL =", sync_db_url)

config.set_main_option("sqlalchemy.url", sync_db_url))

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
