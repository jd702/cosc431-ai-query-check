# SQL Security Audit Checklist (D2 Step 5)

Review **every** AI-generated query by hand. `notebooks/02` gives a first-pass `auto_*` flag for each check. The audit itself is the manual review you record in `results/security_audit.csv`:
- `reviewer`: your initials
- `reviewer_verdict`: `PASS` or `FLAG`
- `reviewer_notes`: one short sentence

| # | Check | What to look for | Why it matters |
|---|---|---|---|
| 1 | **Stacked statement** | A `;` followed by more SQL, e.g. `SELECT … ; DROP TABLE …` | A second statement can modify or destroy data |
| 2 | **Tautology** | Conditions that are always true: `OR 1=1`, `OR 'a'='a'`, `OR TRUE` | Bypasses the intended filter, so every row is returned |
| 3 | **Comment marker** | `--` or `/* … */` in the middle of the query | Can cut off the rest of the query, such as an access-control condition |
| 4 | **Unexpected UNION SELECT** | A `UNION SELECT` the question didn't need, especially one that reads another table | Can pull in data the user shouldn't see |

**Auto-flag vs. your verdict:** an auto-flag isn't automatically a problem. A single trailing `;` is harmless, and a `UNION` can be a legitimate answer. Also flag anything suspicious the checks don't cover, such as a query that writes data (`INSERT`, `UPDATE`, `DELETE`, `DROP`) when the question only asked to read.

Put the best flagged examples on your presentation slides.
