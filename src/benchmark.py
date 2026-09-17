"""Timing for the four schema/index conditions (D2 Step 6)."""
import sqlite3
import timeit
from typing import List


def time_query(db_path, sql: str, repeat: int = 5, number: int = 20) -> float:
    """Best-of-`repeat` average seconds per execution (best-of reduces noise)."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(sql).fetchall()  # warm the page cache
        runs = timeit.repeat(lambda: conn.execute(sql).fetchall(), repeat=repeat, number=number)
        return min(runs) / number
    finally:
        conn.close()


def apply_indexes(db_path, statements: List[str]) -> None:
    conn = sqlite3.connect(db_path)
    try:
        for stmt in statements:
            conn.execute(stmt)
        conn.execute("ANALYZE")
        conn.commit()
    finally:
        conn.close()


def drop_indexes(db_path, names: List[str]) -> None:
    conn = sqlite3.connect(db_path)
    try:
        for name in names:
            conn.execute(f'DROP INDEX IF EXISTS "{name}"')
        conn.commit()
    finally:
        conn.close()


def query_plan(db_path, sql: str) -> str:
    conn = sqlite3.connect(db_path)
    try:
        return "\n".join(r[-1] for r in conn.execute(f"EXPLAIN QUERY PLAN {sql}"))
    finally:
        conn.close()
