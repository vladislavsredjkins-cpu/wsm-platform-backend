from enum import Enum

class CoachLevel(str, Enum):
    COACH_1 = "COACH_1"  # National Coach
    COACH_2 = "COACH_2"  # International Coach
    COACH_3 = "COACH_3"  # Elite Coach

COACH_LEVEL_LABELS = {
    CoachLevel.COACH_1: "National Coach — Level 1",
    CoachLevel.COACH_2: "International Coach — Level 2",
    CoachLevel.COACH_3: "Elite Coach — Level 3",
}
