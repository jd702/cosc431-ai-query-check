# AI Query Check: Evaluating LLM-Generated SQL
*Team: Jelani Denmark, Joshua Sanders, Isaiah Washington, Maxwell Amakor*

> **Status (2026-11-19).** Section 4 (Performance) is complete and backed by
> `results/performance.csv`. Sections 1, 2, 3 and 5 are **not** complete: the models have not
> been run yet, so no generated SQL exists to grade or audit. Draft text written before the data
> existed is kept below under clearly marked headings and must be rewritten against real results
> before submission.

## 1. Methodology (B)
- Database: Chinook (SQLite), normalized and denormalized versions
- Questions: 20 adapted from Spider (`chinook_1`); 6 easy / 14 medium; 7 lookup, 7 join,
  5 aggregation, 1 subquery
- Models: **fill in exact model names and the date they were run**
- Prompt: the schema DDL plus the question, asking for SQL only (see `results/prompt_example.txt`)
- Grading: compared result sets, not SQL text. Row order counted only where the question
  required it.

## 2. Correctness (B + D)

> ⬜ **Blocked** — fill in after notebook 02 Step 3 and Step 4 have been run.

| Model | Correct | Score |
|---|---|---|
| Gemini | | /20 |
| Llama | | /20 |

Error types (wrong table, missed join condition, wrong aggregation, …) with examples from
`results/correctness.csv`.

## 3. Security findings (C)

> ⬜ **Blocked** — no generated SQL exists yet, so nothing has been audited. Fill in from
> `results/security_audit.csv` after the models run.

To report once the audit is done:
- Number of queries flagged per model and per check (stacked statement, tautology, comment
  marker, UNION SELECT)
- 1–3 flagged examples with an explanation
- Where the automatic pre-screen disagreed with the manual review

### Draft written before any model output existed — rewrite against real data

*The following was drafted in advance. It describes expectations, not findings, and must not be
submitted as results.*

- Expectation: queries should be read-only `SELECT` statements; no `DROP`, `DELETE` or `UPDATE`
  was requested by any prompt.
- Risks to watch for: hallucinated tables or columns, excessively broad queries returning
  unintended data, and Cartesian products caused by missing join conditions.
- Manual review remains necessary regardless of what the automatic pre-screen reports.

## 4. Performance (A) — complete

Seven benchmark queries were executed against both the normalized and denormalized Chinook
schemas, with and without indexes, measuring execution time in milliseconds. Each figure is the
best of 9 repetitions of 50 executions, taken after a warm-up run; raw data and query plans are
in `results/performance.csv`.

An important methodological point: Chinook ships 11 foreign-key indexes of its own (`IFK_*`).
The benchmark drops those by name before timing the "no index" conditions — otherwise the
baseline is already indexed and the comparison is meaningless.

| Benchmark | Normalized, no index | Normalized, indexed | Denormalized, no index | Denormalized, indexed |
|---|---|---|---|---|
| B01 | 0.039 | 0.009 | 0.074 | 0.018 |
| B02 | 0.073 | 0.009 | 0.105 | 0.009 |
| B03 | 0.055 | 0.040 | 0.203 | 0.131 |
| B04 | 0.061 | 0.004 | 0.107 | 0.004 |
| B05 | 0.005 | 0.004 | 0.005 | 0.004 |
| B06 | 0.133 | 0.032 | 0.093 | 0.029 |
| B07 | 0.006 | 0.005 | 0.006 | 0.005 |

### Impact of indexing

Indexing improved every query, with no exceptions. The gains ranged from 1.04× (B07) to 28×
(B04, denormalized). `EXPLAIN QUERY PLAN` shows why: without the index SQLite reports `SCAN`
over the whole table, and with it the plan changes to `SEARCH … USING INDEX`.

The largest gains came from queries filtering on a non-key column of a large table — B04 counts
tracks by media type name across 3,503 rows, and B02 averages prices for one genre. The smallest
gains came from B05 and B07, which already touch only the 59-row `Customer` table, where a full
scan is cheap enough that an index saves almost nothing.

### Impact of denormalization

Denormalization helped in only one of seven cases. B06 (albums containing tracks priced above 1)
was faster denormalized, 0.093 ms against 0.133 ms unindexed, because `TrackFlat` already stores
album and track data together.

Every other query was **slower** on the denormalized schema. This is the most interesting result
of the experiment and it is worth stating plainly: removing joins did not pay off at this data
size. The flat tables are larger — `TrackFlat` holds 3,503 wide rows against `Album`'s 347 — so
the scan cost of the extra rows exceeded the join cost that denormalization eliminated. B03 is
the clearest case, at 0.203 ms denormalized against 0.055 ms normalized, because grouping artists
over `TrackFlat` processes one row per track where the normalized version processes one row per
album.

Indexing mattered far more than schema shape in every single case.

### Cost of denormalization

Beyond the timing results, the flat tables carry the redundancy costs documented in Deliverable 1:
artist names, album titles and customer details repeat across many rows, the database grows from
984 KB to 1.7 MB (73% larger), and update, insert and delete anomalies become possible. On this
database the team paid that cost and, for six of seven queries, got slower reads in return.

## 5. Conclusions (D)

> ⬜ **Blocked** — conclusions about model trustworthiness require correctness and security
> results that do not exist yet. Rewrite once sections 2 and 3 are filled in.

### Draft written before any model output existed — rewrite against real data

*Drafted in advance; these are general safeguards, not conclusions drawn from our results.*

Safeguards worth recommending for any text-to-SQL deployment:
- Human review before execution
- Read-only database permissions
- Automated result verification against expected outputs
- Query plan inspection for expensive operations
- Restrictions on modification statements such as `UPDATE`, `DELETE` and `DROP`

## 6. Limitations

- Each model is run once per question, though LLM output is non-deterministic.
- The question set is small (20) and contains only easy and medium difficulty.
- The security audit is a manual, conceptual review rather than static analysis.
- Timings come from a single laptop, and Chinook is a small database, which limits how far the
  normalized-versus-denormalized differences generalize.
- Absolute timings are in fractions of a millisecond, so ratios are more meaningful than
  differences; a noisier measurement method produced contradictory results before the repetition
  count was raised.
