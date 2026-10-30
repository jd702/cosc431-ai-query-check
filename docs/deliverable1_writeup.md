# Deliverable 1 Write-up

## Schema choice

We chose **Chinook**, a digital media store, over Sakila. It is the smaller of the two options
(11 tables against Sakila's 16), which let us spend our time on the evaluation rather than on
learning an unfamiliar schema, and it ships as a single SQLite script so every team member can
rebuild an identical database with one command (`python scripts/setup_db.py`). Chinook is also
represented in the Spider benchmark as `chinook_1`, so the questions we adapted were written
against the same table and column names we query, which kept adaptations minimal.

| Table | Rows | Role |
|---|---|---|
| Artist | 275 | Recording artists |
| Album | 347 | Albums, each belonging to one artist |
| Track | 3,503 | Individual tracks, the largest table |
| Genre | 25 | Track genres |
| MediaType | 5 | Encoding formats |
| Playlist | 18 | Named playlists |
| PlaylistTrack | 8,715 | Many-to-many bridge between playlists and tracks |
| Customer | 59 | Customers, each assigned a support rep |
| Employee | 8 | Staff, with a self-referencing `ReportsTo` hierarchy |
| Invoice | 412 | Customer invoices |
| InvoiceLine | 2,240 | Line items on each invoice |

See [diagrams.md](diagrams.md) for the ER diagram. The relationships give us the variety the
project needs: simple one-to-many chains (Artist → Album → Track), a many-to-many bridge
(PlaylistTrack), a self-referencing hierarchy (Employee.ReportsTo), and nullable foreign keys
(Track.AlbumId, Track.GenreId, Customer.SupportRepId) that make join choice matter. The
Customer → Invoice → InvoiceLine → Track path is four tables deep, which is what makes the
denormalization and indexing comparisons in Deliverable 2 meaningful.

The schema as distributed is already in 3NF, so no normalization work was required to reach it.
That is why Deliverable 1's normalization work runs in the other direction: we deliberately break
3NF to build the denormalized variant described below. Chinook also ships 11 foreign-key indexes
of its own (`IFK_*`), which we had to account for when designing the performance test.

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

## Denormalized Schema

The normalized Chinook schema is already in 3NF, so the variant in `sql/denormalized_schema.sql` deliberately reintroduces redundancy by collapsing the three join paths our 20 benchmark questions use most often. Both versions live in `data/chinook_denorm.db`, so the same gold queries can run against either one.

### Overview

| Flat Table | Merges | Serves | Rows |
| --- | --- | --- | --- |
| `TrackFlat` | Track + Album + Artist + Genre + MediaType | Q09, Q10, Q13, Q14, Q15, Q20 | 3,503 |
| `SalesFlat` | InvoiceLine + Invoice + Customer + Track | Q02, Q07, timing queries | 2,240 |
| `CustomerFlat` | Customer + Support Representative Employee | Q11, Q12, Q16 | 59 |

* * *

## Dependencies and Normal Form Violations

### TrackFlat

**Primary Key:** `TrackId`

#### Dependencies

-   `TrackId → AlbumId`
-   `AlbumId → AlbumTitle, ArtistId`
-   `ArtistId → ArtistName`
-   `GenreId → GenreName`
-   `MediaTypeId → MediaTypeName`

#### Normal Form Violated

`TrackId → AlbumTitle` exists only through the transitive path:

```plaintext
TrackId → AlbumId → AlbumTitle
```

The same pattern exists for artist, genre, and media type data. Because non-key attributes depend on other non-key attributes, this table **violates 3NF**.

It remains in **2NF** because the primary key contains a single attribute, so partial dependencies cannot occur.

#### Redundancy Example

-   "Iron Maiden" is stored 213 times.
-   "U2" is stored 135 times.

* * *

### SalesFlat

**Primary Key:** `InvoiceLineId`

#### Dependencies

-   `InvoiceLineId → InvoiceId`
-   `InvoiceId → InvoiceDate, BillingCity, BillingCountry, InvoiceTotal, CustomerId`
-   `CustomerId → CustomerFirstName, CustomerLastName, CustomerAddress, CustomerCountry`

#### Normal Form Violated

This creates chained transitive dependencies:

```plaintext
InvoiceLineId → InvoiceId → CustomerId
InvoiceLineId → InvoiceId → CustomerId → Customer Information
```

Because customer details are dependent on another non-key attribute (`CustomerId`), the table **violates 3NF**.

#### Redundancy Example

-   One invoice with 14 line items repeats the same customer address 14 times.

* * *

### CustomerFlat

**Primary Key:** `CustomerId`

#### Dependencies

-   `CustomerId → SupportRepId`
-   `SupportRepId → RepFirstName, RepLastName, RepTitle`

#### Normal Form Violated

The dependency chain:

```plaintext
CustomerId → SupportRepId → Representative Information
```

creates a transitive dependency, so the table **violates 3NF**.

#### Redundancy Example

-   With 59 customers and 3 support representatives, each representative's information is stored roughly 20 times.

* * *

## Anomalies Introduced by Denormalization

### Update Anomaly

-   Correcting an artist's name requires updating every song associated with that artist.
-   For example, updating "Iron Maiden" requires modifying 213 rows instead of a single row in the `Artist` table.
-   Partial updates can result in conflicting versions of the same artist name.

### Insert Anomaly

-   `TrackFlat` cannot store an artist or genre unless at least one track exists.
-   `SalesFlat` cannot store a customer who has never made a purchase.
-   Query Q17 ("artists who have not released an album") still depends on the normalized `Artist` table because those artists cannot exist in `TrackFlat`.

### Delete Anomaly

-   Deleting the last track for an artist removes all information about that artist.
-   Deleting the final invoice line of an invoice removes the invoice's date and total.

### Inconsistency Risk

-   `CustomerCountry` and `BillingCountry` both exist in `SalesFlat`.
-   The values can become inconsistent because no constraint guarantees they remain synchronized.

* * *

## Design Decisions and Trade-Offs

### Handling Nullable Foreign Keys

`Track.AlbumId`, `Track.GenreId`, and `Customer.SupportRepId` are flattened using `LEFT JOIN`.

Although the current dataset contains no NULL values in these columns, the schema allows them. Using `INNER JOIN` would silently discard rows and cause the denormalized schema to return different results than the normalized schema.

### Verified Equivalence

Six representative tests (Q07, Q10, Q11, Q14, Q20, and row-count checks) return identical results on both schemas. Any timing differences measured in Deliverable 2 therefore come from schema design rather than differing query results.

### Storage Cost

-   Normalized database size: **984 KB**
-   Denormalized database size: **1.7 MB**
-   Growth: approximately **73% larger**

### Maintaining Both Schemas

The normalized and denormalized tables are stored together.

This is a common denormalization trade-off: additional storage is accepted in exchange for faster, join-free reads that benefit reporting and analytical workloads.
