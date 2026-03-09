import os
import json
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL is not set")

sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
engine = create_engine(sync_db_url)

weight_categories = [
    # MEN
    ("MEN_U70", "U70 kg", "MEN", "MEN", None, 70, False, 1, True),
    ("MEN_U80", "U80 kg", "MEN", "MEN", 70, 80, False, 2, True),
    ("MEN_U95", "U95 kg", "MEN", "MEN", 80, 95, False, 3, True),
    ("MEN_U110", "U110 kg", "MEN", "MEN", 95, 110, False, 4, True),
    ("MEN_PLUS_110", "+110 kg", "MEN", "MEN", 110, None, True, 5, True),

    # WOMEN
    ("WOMEN_U55", "U55 kg", "WOMEN", "WOMEN", None, 55, False, 1, True),
    ("WOMEN_U65", "U65 kg", "WOMEN", "WOMEN", 55, 65, False, 2, True),
    ("WOMEN_U75", "U75 kg", "WOMEN", "WOMEN", 65, 75, False, 3, True),
    ("WOMEN_U85", "U85 kg", "WOMEN", "WOMEN", 75, 85, False, 4, True),
    ("WOMEN_PLUS_85", "+85 kg", "WOMEN", "WOMEN", 85, None, True, 5, True),

    # PARA MEN
    ("PARA_MEN_U49", "Up to 49kg", "PARA", "MEN", None, 49, False, 1, True),
    ("PARA_MEN_U54", "Up to 54kg", "PARA", "MEN", 49, 54, False, 2, True),
    ("PARA_MEN_U59", "Up to 59kg", "PARA", "MEN", 54, 59, False, 3, True),
    ("PARA_MEN_U65", "Up to 65kg", "PARA", "MEN", 59, 65, False, 4, True),
    ("PARA_MEN_U72", "Up to 72kg", "PARA", "MEN", 65, 72, False, 5, True),
    ("PARA_MEN_U80", "Up to 80kg", "PARA", "MEN", 72, 80, False, 6, True),
    ("PARA_MEN_U88", "Up to 88kg", "PARA", "MEN", 80, 88, False, 7, True),
    ("PARA_MEN_U97", "Up to 97kg", "PARA", "MEN", 88, 97, False, 8, True),
    ("PARA_MEN_U107", "Up to 107kg", "PARA", "MEN", 97, 107, False, 9, True),
    ("PARA_MEN_PLUS_107", "Over 107kg", "PARA", "MEN", 107, None, True, 10, True),

    # PARA WOMEN
    ("PARA_WOMEN_U41", "Up to 41kg", "PARA", "WOMEN", None, 41, False, 1, True),
    ("PARA_WOMEN_U45", "Up to 45kg", "PARA", "WOMEN", 41, 45, False, 2, True),
    ("PARA_WOMEN_U50", "Up to 50kg", "PARA", "WOMEN", 45, 50, False, 3, True),
    ("PARA_WOMEN_U55", "Up to 55kg", "PARA", "WOMEN", 50, 55, False, 4, True),
    ("PARA_WOMEN_U61", "Up to 61kg", "PARA", "WOMEN", 55, 61, False, 5, True),
    ("PARA_WOMEN_U67", "Up to 67kg", "PARA", "WOMEN", 61, 67, False, 6, True),
    ("PARA_WOMEN_U73", "Up to 73kg", "PARA", "WOMEN", 67, 73, False, 7, True),
    ("PARA_WOMEN_U79", "Up to 79kg", "PARA", "WOMEN", 73, 79, False, 8, True),
    ("PARA_WOMEN_U86", "Up to 86kg", "PARA", "WOMEN", 79, 86, False, 9, True),
    ("PARA_WOMEN_PLUS_86", "Over 86kg", "PARA", "WOMEN", 86, None, True, 10, True),
]

team_rules = [
    (
        "TEAM_SPLIT_110",
        "Team ±110",
        "Two-athlete team: one athlete up to 110 kg, second athlete over 110 kg",
        {
            "athletes_per_team": 2,
            "rules": [
                {"athlete_no": 1, "max_weight": 110},
                {"athlete_no": 2, "min_weight": 110},
            ],
        },
        1,
        True,
    ),
]

with engine.begin() as conn:
    for row in weight_categories:
        conn.execute(
            text("""
                INSERT INTO weight_categories
                (code, name, division_type, sex_scope, weight_min_kg, weight_max_kg, is_open_upper, sort_order, is_active)
                VALUES
                (:code, :name, :division_type, :sex_scope, :weight_min_kg, :weight_max_kg, :is_open_upper, :sort_order, :is_active)
                ON CONFLICT (code) DO NOTHING
            """),
            {
                "code": row[0],
                "name": row[1],
                "division_type": row[2],
                "sex_scope": row[3],
                "weight_min_kg": row[4],
                "weight_max_kg": row[5],
                "is_open_upper": row[6],
                "sort_order": row[7],
                "is_active": row[8],
            }
        )

    for row in team_rules:
        conn.execute(
            text("""
                INSERT INTO team_rules
                (code, name, description, member_rules, sort_order, is_active)
                VALUES
                (:code, :name, :description, :member_rules, :sort_order, :is_active)
                ON CONFLICT (code) DO NOTHING
            """),
            {
                "code": row[0],
                "name": row[1],
                "description": row[2],
                "member_rules": json.dumps(row[3]),
                "sort_order": row[4],
                "is_active": row[5],
            }
        )

print("Seed completed")