# Formal Query Notation (Deliverable 1, Step 4)

Five of our benchmark queries written in relational algebra and tuple relational calculus, with
a comparison to the SQL. Each uses the verified gold SQL from `data/questions.json` exactly as
submitted, so the IDs below match the benchmark.

Operators: σ selection, π projection, ⋈ natural/theta join, γ grouping and aggregation,
ρ rename, − set difference, ∪ union, ∩ intersection.

---

## Q06 — What are the invoice dates for customers with the first name Astrid and the last name Gruber?

**SQL**
```sql
SELECT T2.InvoiceDate
FROM CUSTOMER AS T1
JOIN INVOICE AS T2 ON T1.CustomerId = T2.CustomerId
WHERE T1.FirstName = 'Astrid' AND T1.LastName = 'Gruber'
```

**Relational algebra**
```
π_InvoiceDate( σ_{FirstName='Astrid' ∧ LastName='Gruber'}( Customer ⋈_{Customer.CustomerId = Invoice.CustomerId} Invoice ) )
```

A more efficient but equivalent form pushes the selection below the join, which is exactly what
a query optimizer does:
```
π_InvoiceDate( ( σ_{FirstName='Astrid' ∧ LastName='Gruber'}(Customer) ) ⋈_{CustomerId} Invoice )
```

**Comparison.** The algebra makes evaluation *order* explicit: the first form filters after
building the whole join, the second filters first. Both return the same relation, which is why
the rewrite is a legal optimization. The SQL states no order at all — it declares the result and
leaves the plan to SQLite, and the plan we actually measured in Deliverable 2 confirms the
engine chooses the second form. The algebra also hides something the SQL shows: `⋈_{CustomerId}`
has to be written as an explicit theta-join condition, because a natural join would silently
match on every same-named column the two relations share.

---

## Q10 — Count the number of tracks that are of the media type 'AAC audio file'.

**SQL**
```sql
SELECT COUNT(*)
FROM MEDIATYPE AS T1
JOIN TRACK AS T2 ON T1.MediaTypeId = T2.MediaTypeId
WHERE T1.Name = 'AAC audio file'
```

**Relational algebra**
```
γ_{COUNT(TrackId) → TrackCount}( σ_{Name='AAC audio file'}( MediaType ⋈_{MediaTypeId} Track ) )
```

**Comparison.** `COUNT(*)` in SQL counts *rows*, including duplicates and rows that are entirely
NULL. The algebra forces a decision the SQL leaves implicit: we wrote `COUNT(TrackId)`, which
counts non-NULL values of a specific attribute. The two agree here only because `TrackId` is a
primary key and can never be NULL. The algebra also exposes that this is bag, not set,
semantics: pure relational algebra treats relations as sets, so a strict reading would
deduplicate and give the wrong count. γ is an extension to the algebra precisely because SQL's
aggregation needs multisets.

---

## Q14 — Which artist has the most albums?

**SQL**
```sql
SELECT T2.NAME
FROM ALBUM AS T1
JOIN ARTIST AS T2 ON T1.ArtistId = T2.ArtistId
GROUP BY T2.Name
ORDER BY COUNT(*) DESC
LIMIT 1
```

**Relational algebra**
```
A ← γ_{ArtistId, Name; COUNT(AlbumId) → AlbumCount}( Artist ⋈_{ArtistId} Album )
M ← γ_{MAX(AlbumCount) → MaxCount}(A)
Result ← π_Name( σ_{AlbumCount = MaxCount}( A × M ) )
```

**Comparison.** This is the clearest case of the notation exposing what the SQL hides. There is
no `LIMIT` in relational algebra, so "the most" has to be expressed as a self-comparison against
the maximum: aggregate once, take the max, then join back. That reveals a real difference in
meaning. The algebra returns **every** artist tied for the maximum, while `ORDER BY ... LIMIT 1`
returns exactly one row and silently picks an arbitrary winner among ties. Our gold answer is
Iron Maiden with 21 albums, and no artist ties it, so the two forms agree on this data — but
they are not the same query, and that is only true by luck of the data. Grouping by `Name`
rather than `ArtistId` carries the same hazard: two artists with the same name would be merged.

---

## Q17 — Count the number of artists who have not released an album.

**SQL**
```sql
SELECT COUNT(*)
FROM ARTIST AS T1
WHERE NOT EXISTS (SELECT 1 FROM ALBUM AS T2 WHERE T2.ArtistId = T1.ArtistId)
```

**Relational algebra** (an antijoin, expressed as a difference)
```
γ_{COUNT(ArtistId)}( π_ArtistId(Artist) − π_ArtistId(Album) )
```

**Tuple relational calculus**
```
{ t | ∃ a ∈ Artist ( t.ArtistId = a.ArtistId ∧ ¬∃ b ∈ Album ( b.ArtistId = a.ArtistId ) ) }
```

**Comparison.** The SQL expresses the absence of a match with a correlated subquery, which reads
procedurally: for each artist, go look for an album. The algebra says the same thing in one
operator, a set difference on the projected keys, which makes it obvious that this is a *set*
operation on `ArtistId` values and nothing more. The calculus form is the most literal, mapping
`NOT EXISTS` directly onto `¬∃`. The algebra also explains why Joshua changed the original
Spider gold SQL from `NOT IN` to `NOT EXISTS` (see the adaptations table): set difference is
well defined on NULL-free key sets, but SQL's `NOT IN` returns UNKNOWN rather than TRUE if the
inner list contains a single NULL, which would make the count silently wrong. The formal
notation has no three-valued logic, so the hazard simply does not exist in it — the notation
hides a problem the SQL has to be careful about.

---

## Q02 — Find all the customer last names that do not have invoice totals larger than 20.

**SQL**
```sql
SELECT LastName FROM CUSTOMER
EXCEPT
SELECT T1.LastName FROM CUSTOMER AS T1
JOIN Invoice AS T2 ON T1.CustomerId = T2.CustomerId
WHERE T2.total > 20
```

**Relational algebra**
```
π_LastName(Customer) − π_LastName( σ_{Total > 20}( Customer ⋈_{CustomerId} Invoice ) )
```

**Comparison.** Here the SQL and the algebra line up almost symbol for symbol, since `EXCEPT`
*is* the difference operator. What the notation makes explicit is the level the difference
operates at: both sides are projected down to `LastName`, so the operation subtracts **names**,
not **customers**. A customer whose last name is shared with a big spender would be removed too.
Projecting first and subtracting after is not the same as subtracting customers and then
projecting. In our data, all 59 customers have distinct last names, so the result is correct —
but the algebra shows that correctness depends on the data, not on the query. It also makes
`EXCEPT`'s implicit deduplication visible: set difference returns a set, which is why 55 names
come back rather than one row per customer.
