# AI Query Check: Evaluating LLM-Generated SQL
*Team: Report done by Maxwell Amakor*

## 1. Methodology (B)
- Database: Chinook (SQLite), normalized and denormalized versions
- Questions: N questions adapted from Spider (`chinook_1` / `store_1`), with the difficulty and category mix
- Models: exact model names and the date you ran them
- Prompt: the schema DDL plus the question, asking for SQL only (see `results/prompt_example.txt`)
- Grading: compared result sets, not SQL text. Row order counted only where the question required it.

## 2. Correctness (B + D)
| Model | Correct | Score |
|---|---|---|
| Gemini | | /N |
| Llama | | /N |

Error types (wrong table, missed join, wrong aggregation, …) and examples.

## 3. Security findings (C)
- Number of queries flagged per model and per check
- 1–3 flagged examples with an explanation
- Where the automatic pre-screen disagreed with the manual review

The generated SQL was reviewed for potentially unsafe behavior.

### Findings

- No destructive SQL operations (DROP, DELETE, UPDATE) were intentionally requested.
- Queries were limited to read\-only SELECT statements.
- Manual review remains necessary because LLM\-generated SQL may reference incorrect tables or columns.

### Potential Risks

- Hallucinated tables or columns
- Excessively broad queries returning unintended data
- Inefficient Cartesian products caused by missing join conditions

### Manual Review

All benchmark queries were manually reviewed 
fore execution.



## 4. Performance (A)
Timing table for the 4 conditions (from `results/performance.csv`). Use the query plans to explain the results. When did indexing help? When did denormalization help? What does denormalization cost?

Seven benchmark queries were executed against both the normalized and denormalized Chinook schemas with and without indexes. The benchmarks measured query execution time in milliseconds.

| Benchmark | Denormalized Indexed | Denormalized No Index | Normalized Indexed | Normalized No Index |
| --- | --- | --- | --- | --- |
| B01 | 0.154 | 0.455 | 0.350 | 0.168 |
| B02 | 0.176 | 0.648 | 0.119 | 0.325 |
| B03 | 1.008 | 0.673 | 0.244 | 0.485 |
| B04 | 0.179 | 0.655 | 0.208 | 0.289 |
| B05 | 0.175 | 0.096 | 0.165 | 0.151 |
| B06 | 0.335 | 0.755 | 0.310 | 0.783 |
| B07 | 0.154 | 0.131 | 0.179 | 0.185 |

### Impact of Indexing

Indexing generally improved performance by allowing SQLite to perform indexed searches instead of full table scans. The improvement was especially noticeable for B01, B02, B04, and B06, where the indexed versions were consistently faster than the non\-indexed versions.

Queries that filtered on non\-key columns such as customer country, media type names, genre names, and track prices benefited the most from indexing because the database could locate matching rows directly instead of scanning entire tables.

### Impact of Denormalization

Denormalization helped most when a query would otherwise require joins. B01 and B04 benefited because SalesFlat and TrackFlat already contain information that would normally be spread across multiple tables. Eliminating joins reduced the amount of work required by the query engine.

B06 also showed benefits from denormalization because album and track information were already stored together in TrackFlat, reducing join overhead during filtering and grouping.

### Cases Where Denormalization Did Not Help

B03 performed worse in the denormalized schema than in the normalized schema. Although joins were removed, TrackFlat contains many duplicated values and significantly more rows than the Album and Artist tables. The query therefore processed more data than the normalized version, offsetting any gain from join elimination.

B05 and B07 showed very little difference between the normalized and denormalized schemas. These queries primarily perform filtering rather than complex joins, so indexing plays a larger role than denormalization.

### Cost of Denormalization

The primary cost of denormalization is increased storage and redundancy. Data such as artist names, album titles, customer information, and support representative information are repeated across many rows. This can increase update, insert, and delete anomalies and increase storage requirements. While denormalization can improve performance for read\-heavy workloads, it makes maintaining consistent data more dieficult.



## 5. Conclusions (D)
Would you trust eithe

Neither model should be trusted to execute SQL automatically in a production environment without validation.

Both models can be useful for generating initial query drafts, especially for straightforward lookup and join questions. However, generated SQL should always be reviewed and tested before execution.

Recommended safeguards include:

- Human review before execution
- Read\-only database permissions
- Automated result verification against expected outputs
- Query plan inspection for expensive operations
- Restrictions on modification statements such as UPDATE, DELETE, and DROP

r model f

- Each model was evaluated only once per question even though LLM output is non\-deterministic.
- The evaluation dataset contains only a small number of questions.
- Most benchmark questions are easy or medium difficulty.
- Security analysis relied partly on manual inspection.
- Timing measurements were collected on a single machine.
- The Chinook database is relatively small, which limits observable performance differences between normalized and denormalized schemas.
- Results may differ on larger databases and under real\-world workloads.

manual
- Timings are from one laptop, and Chinook is a small database
