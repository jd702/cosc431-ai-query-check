# Deliverable 1 Write-up

## Schema choice
<!-- Why Chinook? Tables, relationships, row counts (setup_db.py prints them). -->

## Question sources
<!-- Which Spider databases (chinook_1 / store_1), how many from each, how you selected them,
     difficulty/category mix. -->
     Selected 20 questions from the Spider benchmark and used chinook_1 database. Focused on easy and medium difficuly questions.

## Adaptations
<!-- For each question you changed: what you changed and why (names, wording, SQL dialect). -->

| ID | Spider source             | Change made |
|----|---------------------------|-------------|
|Q05 |train_spider.json,index 864|Changed wording to "List the phone numbers of all employees" so that the question directly matches the SQL|
|Q12 |train_spider.json,index 870|Changed the question and gold SQL, so that the query returns the employee's first name and SupportRepId|
|Q13 |train_spider.json,index 837|Adjusted the Group By clause to include the media type information for an aggregation.|
|Q15 |train_spider.json,index 840|Added the album title to the Group BY so that the selected album is properly grouped with the album ID|
|Q16 |train_spider.json,index 872|Changed the INNER JOIN to a LEFT JOIN so employees with zero customers are not excluded. The question was clarified to include employees who serve no customers|
|Q17 |train_spider.json,index 888|Changed the subquery from NOT IN to NOT EXISTS to express the condition while avoiding NULL behavior.|
Q|20 |train_spider.json,index 888|Adapted the question and SQL to the database.|
## Denormalized schema

The normalized Chinook schema is already in 3NF, so the variant in
`sql/denormalized_schema.sql` deliberately reintroduces redundancy by collapsing the three
join paths our 20 benchmark questions use most often. Both versions live in
`data/chinook_denorm.db`, so the same gold queries can run against either one.

| Flat table | Merges | Serves | Rows |
|---|---|---|---|
| `TrackFlat` | Track + Album + Artist + Genre + MediaType | Q09, Q10, Q13, Q14, Q15, Q20 | 3,503 |
| `SalesFlat` | InvoiceLine + Invoice + Customer + Track | Q02, Q07, timing queries | 2,240 |
| `CustomerFlat` | Customer + support-rep Employee | Q11, Q12, Q16 | 59 |

### Dependencies and normal forms broken

**TrackFlat** (key `TrackId`). `TrackId → AlbumId` and `AlbumId → AlbumTitle, ArtistId`, so
`TrackId → AlbumTitle` only transitively. The same holds for `ArtistId → ArtistName`,
`GenreId → GenreName` and `MediaTypeId → MediaTypeName`. Non-key attributes therefore depend
on other non-key attributes, which **violates 3NF** (it stays in 2NF, since the key is a single
attribute and no partial dependencies are possible). The redundancy is substantial: "Iron
Maiden" is now stored 213 times, "U2" 135 times.

**SalesFlat** (key `InvoiceLineId`). `InvoiceLineId → InvoiceId` and
`InvoiceId → InvoiceDate, BillingCity, BillingCountry, InvoiceTotal, CustomerId`, then
`CustomerId → CustomerFirstName, CustomerLastName, CustomerAddress, CustomerCountry`. Two
chained transitive dependencies, so this also **violates 3NF**. One invoice with 14 line items
repeats that customer's address 14 times.

**CustomerFlat** (key `CustomerId`). `CustomerId → SupportRepId → RepFirstName, RepLastName,
RepTitle`, a transitive dependency that **violates 3NF**. With 59 customers served by 3 reps,
each rep's name is stored about 20 times.

### Anomalies this creates

- **Update anomaly.** Correcting an artist's name now means updating every track row for that
  artist (213 rows for Iron Maiden) instead of one row in `Artist`. A partial update leaves the
  database with two spellings of the same artist and no way to tell which is right.
- **Insert anomaly.** `TrackFlat` cannot record an artist or genre that has no tracks yet, and
  `SalesFlat` cannot record a customer who has never been invoiced, because there is no row to
  put them in without inventing a fake track or invoice line. Note that Q17 ("artists who have
  not released an album") depends on exactly those artists existing, so it still needs the
  normalized `Artist` table.
- **Delete anomaly.** Deleting the last line item of an invoice erases that invoice's date and
  total, and deleting an artist's last track erases the artist entirely.
- **Inconsistency risk.** `CustomerCountry` and `BillingCountry` are both in `SalesFlat` and can
  now disagree, with no constraint to stop it.

### Design decisions and cost

- Nullable foreign keys (`Track.AlbumId`, `Track.GenreId`, `Customer.SupportRepId`) are
  flattened with `LEFT JOIN`. The current data has no NULLs there, but the schema allows them,
  and an `INNER JOIN` would silently drop rows and make the denormalized copy return different
  answers from the normalized one.
- **Verified equivalence:** six representative queries (Q07, Q10, Q11, Q14, Q20 and row counts)
  return identical results on both schemas, so any timing difference we measure in Deliverable 2
  comes from the schema and not from different answers.
- **Storage cost:** the database grows from 984 KB to 1.7 MB, roughly 73% larger, for the same
  information.
- The normalized tables are kept alongside the flat ones. That is itself a denormalization
  trade-off: we accept duplicated storage to keep the join-free read path, which is the standard
  argument for a read-optimized reporting table.
