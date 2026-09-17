"""Offline sanity checks — no API keys or downloads needed.

    python -m unittest discover tests
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.benchmark import apply_indexes, drop_indexes, query_plan, time_query
from src.grading import results_match, run_query
from src.security import prescreen


class GradingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / "t.db"
        conn = sqlite3.connect(cls.db)
        conn.executescript(
            "CREATE TABLE Artist(ArtistId INTEGER PRIMARY KEY, Name TEXT);"
            "INSERT INTO Artist VALUES (1,'AC/DC'),(2,'Accept'),(3,'Aerosmith');"
        )
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_equivalent_queries_match(self):
        gold, _ = run_query(self.db, "SELECT Name FROM Artist WHERE ArtistId < 3")
        pred, _ = run_query(self.db, "SELECT a.Name AS n FROM Artist a WHERE a.Name LIKE 'Ac%' ORDER BY 1 DESC")
        self.assertTrue(results_match(gold, pred))
        self.assertFalse(results_match(gold, pred, ordered=True))

    def test_wrong_result_and_errors(self):
        gold, _ = run_query(self.db, "SELECT Name FROM Artist")
        pred, _ = run_query(self.db, "SELECT Name FROM Artist LIMIT 2")
        self.assertFalse(results_match(gold, pred))
        rows, err = run_query(self.db, "SELECT * FROM Nope")
        self.assertIsNone(rows)
        self.assertIn("no such table", err)
        self.assertFalse(results_match(gold, rows))

    def test_read_only_and_no_stacked_execution(self):
        rows, err = run_query(self.db, "SELECT 1; DROP TABLE Artist")
        self.assertIsNotNone(err)
        rows, err = run_query(self.db, "DELETE FROM Artist")
        self.assertIsNotNone(err)
        self.assertEqual(run_query(self.db, "SELECT COUNT(*) FROM Artist")[0], [(3,)])

    def test_benchmark_helpers(self):
        apply_indexes(self.db, ["CREATE INDEX idx_name ON Artist(Name)"])
        self.assertIn("idx_name", query_plan(self.db, "SELECT * FROM Artist WHERE Name='AC/DC'"))
        drop_indexes(self.db, ["idx_name"])
        self.assertGreater(time_query(self.db, "SELECT * FROM Artist", repeat=2, number=2), 0)


class SecurityTests(unittest.TestCase):
    def test_clean_query(self):
        self.assertFalse(any(prescreen("SELECT Name FROM Artist WHERE Name = 'a--b; c';").values()))

    def test_flags(self):
        self.assertTrue(prescreen("SELECT 1; DROP TABLE x")["stacked_statement"])
        self.assertTrue(prescreen("SELECT * FROM t WHERE id=5 OR 1=1")["tautology"])
        self.assertTrue(prescreen("SELECT * FROM t WHERE a='x' OR 'a'='a'")["tautology"])
        self.assertFalse(prescreen("SELECT * FROM t WHERE a=1 OR 1=2")["tautology"])
        self.assertFalse(prescreen("SELECT * FROM t WHERE a=1 OR 10=1")["tautology"])
        self.assertTrue(prescreen("SELECT * FROM t -- WHERE owner = 3")["comment_marker"])
        self.assertTrue(prescreen("SELECT a FROM t UNION SELECT password FROM users")["union_select"])


if __name__ == "__main__":
    unittest.main()
