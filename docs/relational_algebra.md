# Formal Query Notation (D1 Step 4)

Pick 3–5 queries that use a join, an aggregation, or a subquery.

Notation: σ (select), π (project), ⋈ (join), γ (group/aggregate), ρ (rename), − (difference), ∪, ∩.
Tuple relational calculus: `{ t | ∃ a ∈ Album ( … ) }`

---

## Q?? — <question text>

**SQL**
```sql

```

**Relational algebra**

```
π_{…}( σ_{…}( R ⋈_{…} S ) )
```

**Comparison:** what does the formal notation make explicit that the SQL hides, or the other way around? (For example: the order of operations, set vs. bag semantics, or how SQL's `NOT IN` hides a set difference.)

---
