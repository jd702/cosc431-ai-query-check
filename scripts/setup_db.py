"""Build the local SQLite databases.

    python scripts/setup_db.py

1. Downloads the official Chinook SQLite script (MIT license) if not cached.
2. Builds data/chinook.db               (normalized — the original schema)
3. Builds data/chinook_denorm.db        (normalized tables + sql/denormalized_schema.sql)
4. Writes sql/normalized_schema.sql     (the CREATE TABLE statements, used in LLM prompts)
"""
import sqlite3
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SQL = ROOT / "sql"
CHINOOK_URL = (
    "https://raw.githubusercontent.com/lerocha/chinook-database/master/"
    "ChinookDatabase/DataSources/Chinook_Sqlite.sql"
)
CACHE = DATA / "Chinook_Sqlite.sql.cache"
NORM_DB = DATA / "chinook.db"
DENORM_DB = DATA / "chinook_denorm.db"


def fetch_script() -> str:
    if not CACHE.exists():
        print(f"Downloading {CHINOOK_URL}")
        urllib.request.urlretrieve(CHINOOK_URL, CACHE)
    return CACHE.read_text(encoding="utf-8-sig")


def build(db_path: Path, script: str) -> sqlite3.Connection:
    db_path.unlink(missing_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(script)
    conn.commit()
    return conn


def dump_ddl(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return ";\n\n".join(r[0] for r in rows) + ";\n"


def main() -> None:
    DATA.mkdir(exist_ok=True)
    script = fetch_script()

    conn = build(NORM_DB, script)
    (SQL / "normalized_schema.sql").write_text(dump_ddl(conn))
    counts = {
        t: conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        for (t,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    }
    conn.close()
    print(f"Built {NORM_DB.name}: " + ", ".join(f"{t}={n}" for t, n in counts.items()))

    denorm_sql = (SQL / "denormalized_schema.sql").read_text()
    conn = build(DENORM_DB, script)
    conn.executescript(denorm_sql)
    conn.commit()
    conn.close()
    print(f"Built {DENORM_DB.name} (normalized tables + denormalized variant)")


if __name__ == "__main__":
    main()
