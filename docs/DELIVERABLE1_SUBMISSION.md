# Deliverable 1 — Submission Index

COSC 431 · AI Query Check · Chinook (SQLite)
Team: Jelani Denmark (pipeline), Joshua Sanders (question set), Isaiah Washington (formal
methods/security), Maxwell Amakor (schema/performance)

Rebuild everything from scratch with: `python scripts/setup_db.py`

| # | Required item | Where it is | Status |
|---|---|---|---|
| 1 | Normalized schema (DDL / CREATE TABLE) | [`sql/normalized_schema.sql`](../sql/normalized_schema.sql) — 11 tables, generated from the live database | ✅ |
| 2 | Denormalized schema variant + explanation of changes | [`sql/denormalized_schema.sql`](../sql/denormalized_schema.sql), explained in [`deliverable1_writeup.md`](deliverable1_writeup.md#denormalized-schema) | ✅ |
| 3 | 15–20 questions, each with verified gold SQL and its result | [`data/questions.json`](../data/questions.json) (20 questions) and [`data/gold_results.json`](../data/gold_results.json) (result sets) | ✅ |
| 4 | 3–5 queries in relational algebra / calculus + comparison | [`docs/relational_algebra.md`](relational_algebra.md) — Q02, Q06, Q10, Q14, Q17 | ✅ |
| 5 | Brief write-up: schema choice, question sources, adaptations | [`docs/deliverable1_writeup.md`](deliverable1_writeup.md) | ✅ |
| — | *Extra, not required:* ER diagram and pipeline diagrams | [`docs/diagrams.md`](diagrams.md) | ✅ |

## Question set at a glance

20 questions adapted from Spider's `chinook_1` database: 6 easy, 14 medium. By type: 7 lookups,
7 joins, 5 aggregations, 1 subquery. All 20 execute against `data/chinook.db` with no errors and
no empty result sets. Seven required adaptation, documented with their Spider indexes in the
write-up.

## How the gold answers were verified

1. `notebooks/01_build_benchmark.ipynb` executes every gold query against the local database and
   writes the result sets to `data/gold_results.json`.
2. The notebook asserts the set is 15–20 questions, has unique IDs, and includes at least one
   subquery.
3. Each result was reviewed by a team member other than its author.
4. Several answers were cross-checked against the raw data independently — for example, "least
   common media type" returns Purchased AAC (7 tracks, fewer than AAC's 11), and "artists with no
   album" returns 71 (275 artists, 204 of which have albums).

## Known limitations

- Questions are easy and medium only, per the project guide's recommendation.
- Two questions (Q13, Q14) use `ORDER BY ... LIMIT 1`, which returns an arbitrary winner if
  values tie. No ties exist in this data, and this is noted in the relational algebra comparison.
- Q02 subtracts last names rather than customers, which is only correct because all 59 customers
  have distinct last names.
- Typos from the original Spider wording were left in place deliberately, to keep the questions
  faithful to the source dataset.

## Not part of Deliverable 1

Running the AI models, correctness scoring, the security audit, the performance benchmark, the
written report, and the in-class presentation are all Deliverable 2. The tooling for them is
already in the repo (`notebooks/02_run_grade_audit_benchmark.ipynb`,
`data/benchmark_queries.json`, `docs/security_checklist.md`, `docs/report_template.md`).
