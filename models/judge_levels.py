from enum import Enum

class JudgeLevel(str, Enum):
    NATIONAL_1 = "NATIONAL_1"          # Национальный 1 категория
    NATIONAL_2 = "NATIONAL_2"          # Национальный 2 категория
    INTERNATIONAL_3 = "INTERNATIONAL_3"  # Международный 3 категория
    INTERNATIONAL_4 = "INTERNATIONAL_4"  # Международный 4 категория (высший)

JUDGE_LEVEL_LABELS = {
    JudgeLevel.NATIONAL_1: "National Judge — Category I",
    JudgeLevel.NATIONAL_2: "National Judge — Category II",
    JudgeLevel.INTERNATIONAL_3: "International Judge — Category III",
    JudgeLevel.INTERNATIONAL_4: "International Judge — Category IV",
}

JUDGE_LEVEL_TIER = {
    JudgeLevel.NATIONAL_1: "national",
    JudgeLevel.NATIONAL_2: "national",
    JudgeLevel.INTERNATIONAL_3: "international",
    JudgeLevel.INTERNATIONAL_4: "international",
}
