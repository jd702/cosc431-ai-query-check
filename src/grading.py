"""Run SQL and compare RESULT SETS (not SQL text) against the gold answer."""
import sqlite3
from collections import Counter
from typing import List, Optional, Tuple


def run_query(db_path, sql: str) -> Tuple[Optional[List[tuple]], Optional[str]]:
    """Execute one query read-only. Returns (rows, error)."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return conn.execute(sql).fetchall(), None
    except (sqlite3.Error, sqlite3.Warning) as e:  # Warning = multiple statements
        return None, f"{type(e).__name__}: {e}"
    finally:
        conn.close()


def _normalize(value):
    if isinstance(value, float):
        return round(value, 2)
    return value


def results_match(gold: List[tuple], pred: Optional[List[tuple]], ordered: bool = False) -> bool:
    """True if pred returns the same rows as gold.

    - Column names/aliases are ignored; column ORDER matters.
    - Row order only matters when ordered=True (set it for questions with ORDER BY
      whose answer depends on order, e.g. "top 5").
    - Duplicates matter (multiset comparison). Floats compared to 2 decimals.
    """
    if pred is None:
        return False
    g = [tuple(_normalize(v) for v in row) for row in gold]
    p = [tuple(_normalize(v) for v in row) for row in pred]
    if ordered:
        return g == p
    return Counter(g) == Counter(p)
