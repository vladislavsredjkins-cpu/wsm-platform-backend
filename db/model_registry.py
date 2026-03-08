from db.base import Base

# импортируем все модели ТОЛЬКО для регистрации таблиц

from models.athlete import Athlete
from models.competition import Competition
from models.competition_class import CompetitionClass
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
from models.category_scheme import CategoryScheme

# новые модели
from models.weight_category import WeightCategory
from models.team_rule import TeamRule

target_metadata = Base.metadata
