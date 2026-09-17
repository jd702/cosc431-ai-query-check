# AI Query Check: Evaluating LLM-Generated SQL
*Team: …*

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

## 4. Performance (A)
Timing table for the 4 conditions (from `results/performance.csv`). Use the query plans to explain the results. When did indexing help? When did denormalization help? What does denormalization cost?

## 5. Conclusions (D)
Would you trust either model for real text-to-SQL use? Under what safeguards?

## 6. Limitations (D)
- Each model was run only once per question, even though LLM output is non-deterministic
- Small question set, with only easy and medium questions
- Security review was manual
- Timings are from one laptop, and Chinook is a small database
