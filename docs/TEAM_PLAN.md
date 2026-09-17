# Team Plan (4 people)

Fill in names on day one. Each role has one **owner** and one **backup**. The backup reviews the owner's work, so everyone learns the whole pipeline before the presentation.

| Role | Name | Backup | Owns |
|---|---|---|---|
| **A. Schema & Performance lead** | | (C) | Chinook setup, denormalized schema + write-up, D2 Step 6 timing |
| **B. Question-set lead** | | (D) | Picking 15–20 Spider questions, gold SQL, notebook 01 |
| **C. Formal Methods & Security lead** | | (A) | Relational algebra/calculus (3–5 queries), D2 Step 5 security audit |
| **D. Pipeline lead** | Jelani Denmark | (B) | `.env`/API setup, notebook 02 Steps 3–4, correctness analysis |

## Status (as of 2026-09-17)

**Done — project scaffolding (Jelani, D):**
- Repo structure, `.gitignore`, `.env.example`, `requirements.txt`, setup instructions (README)
- `scripts/setup_db.py` (builds both SQLite DBs — not yet run against real Chinook)
- Shared code in `src/`: LLM calls, result-set grading, security pre-screen, timing helpers + offline tests (passing)
- Notebook 01 (run/verify gold SQL) and notebook 02 (generate → grade → audit → time) — code written, not yet run on real data
- Empty templates in `docs/` for the write-up, relational algebra, security checklist, report

**Starter examples only — the owner must replace/finish:**
- `data/questions.json` — 2 example questions (need 15–20 real ones) → B + all
- `sql/denormalized_schema.sql` — a sample SalesFlat/TrackFlat design → A
- `data/benchmark_queries.json` — 2 example timing queries → A

**Not started — open for teammates:** everything else in the checklists below
(Spider question selection, gold SQL, relational algebra, D1 write-up, security audit, timing
analysis, report sections, slides).

Everyone writes gold SQL: B picks the questions and splits them across all four people, about 5 each. Everyone also contributes to the report and presentation.

---

## Deliverable 1: start right after the normalization unit

| # | Task | Who | Done |
|---|---|---|---|
| 1 | Everyone: clone the repo, run setup, confirm `python -m unittest discover tests` passes | All | ☐ |
| 2 | Confirm the team uses Chinook (default) | All | ☐ |
| 3 | Shortlist ~25 easy/medium Spider questions from `chinook_1`/`store_1`, then cut to 15–20 with a mix: single-table, 2–3 table joins, aggregation, ≥1 subquery | B | ☐ |
| 4 | Split questions across 4 people. Each person writes gold SQL in `data/questions.json` and fills in `owner` | All | ☐ |
| 5 | Run notebook 01. Each result is checked by someone **other than** its author (peer review log) | B + all | ☐ |
| 6 | Write 3–5 queries in relational algebra/calculus and compare them to the SQL → `docs/relational_algebra.md` | C | ☐ |
| 7 | Finalize `sql/denormalized_schema.sql` and explain each change in NF terms | A | ☐ |
| 8 | Write-up: schema choice, question sources, adaptations → `docs/deliverable1_writeup.md` | A + B | ☐ |
| 9 | Final check against the D1 submission checklist (below) | C | ☐ |

**D1 submission checklist**
- ☐ Normalized DDL: `sql/normalized_schema.sql`
- ☐ Denormalized DDL + explanation: `sql/denormalized_schema.sql`, `docs/deliverable1_writeup.md`
- ☐ 15–20 questions + verified gold SQL + results: `data/questions.json`, `data/gold_results.json`
- ☐ 3–5 RA/RC queries + comparison: `docs/relational_algebra.md`
- ☐ Brief write-up: `docs/deliverable1_writeup.md`

---

## Deliverable 2: after the physical design and security units

| # | Task | Who | Done |
|---|---|---|---|
| 1 | Everyone creates their **own** Gemini + Groq keys in their own `.env` | All | ☐ |
| 2 | Check current model names and rate limits, then update `.env.example` if they changed | D | ☐ |
| 3 | Run notebook 02 Step 3 **once** on one machine, then commit `results/generated_sql.json` so no one else re-runs it | D | ☐ |
| 4 | Step 4: grade, then fill in `why_wrong` for each incorrect query in `results/correctness.csv` | D + B | ☐ |
| 5 | Step 5: manual security audit of **every** generated query → `results/security_audit.csv` | C (+A reviews) | ☐ |
| 6 | Step 6: write 3–5 benchmark queries (joins / WHERE on non-key columns) in `data/benchmark_queries.json`, then run timing | A | ☐ |
| 7 | Report: A writes performance, B methodology + correctness, C security, D conclusions + limitations | All | ☐ |
| 8 | Slides: each person presents their own section. Hold a dry run where everyone explains a section that isn't theirs | All | ☐ |

**D2 submission checklist**
- ☐ Generated SQL from both models: `results/generated_sql.json`
- ☐ Correctness score per model + notes: `results/correctness.csv`
- ☐ Security checklist for every query + flagged examples: `results/security_audit.csv`
- ☐ 4-condition timing + interpretation: `results/performance.csv` + report
- ☐ Written report: `docs/report_template.md`
- ☐ Presentation slides

---

## Working agreements
- **Git:** pull before you start. Commit small changes with clear messages. Only one person edits `questions.json` at a time, so say so in the chat before you do.
- **Weekly check-in** (15 min): what's done, what's blocked, what's next.
- **Never** paste API keys in chat or commit `.env`.
- If you're stuck for more than 30 minutes, ask your backup.
