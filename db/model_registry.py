from db.base import Base

from models.athlete import Athlete
from models.season import Season
from models.competition import Competition
from models.competition_division import CompetitionDivision
from models.competition_discipline import CompetitionDiscipline
from models.participant import Participant
from models.discipline_result import DisciplineResult
from models.discipline_standing import DisciplineStanding
from models.overall_standing import OverallStanding
from models.protest import Protest
from models.competition_division_q import CompetitionDivisionQ
from models.competition_division_snapshot import CompetitionDivisionSnapshot
from models.ranking_award import RankingAward
from models.ranking_entry import RankingEntry
from models.weight_category import WeightCategory
from models.team_rule import TeamRule
from models.country import Country
from models.athlete_sponsor import AthleteSponsor
from models.judge import Judge
from models.judge_certificate import JudgeCertificate
from models.judge_competition import JudgeCompetition
from models.organizer import Organizer
from models.organizer_sponsor import OrganizerSponsor
from models.person import Person
from models.user import User

target_metadata = Base.metadata