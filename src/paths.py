from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SQL = ROOT / "sql"
RESULTS = ROOT / "results"

NORM_DB = DATA / "chinook.db"
DENORM_DB = DATA / "chinook_denorm.db"
QUESTIONS = DATA / "questions.json"
SCHEMA_DDL = SQL / "normalized_schema.sql"
