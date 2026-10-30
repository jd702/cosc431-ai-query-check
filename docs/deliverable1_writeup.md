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

### TrackFlat

**Merged Tables**

-   Track
-   Album
-   Artist
-   Genre
-   MediaType

**Dependencies**

-   AlbumId → AlbumTitle, ArtistId
-   ArtistId → ArtistName
-   GenreId → GenreName
-   MediaTypeId → MediaTypeName

**Normal Form Violated**

-   Violates **3NF (Third Normal Form)** because album, artist, genre, and media type information are stored redundantly in track records through transitive dependencies.

**Update Anomaly**

-   If an artist's name changes, every track row associated with that artist must be updated.
-   If a genre name changes, the modification must be made in multiple rows.

**Insert Anomaly**

-   A new artist, album, genre, or media type cannot be added unless at least one track exists for it.

**Delete Anomaly**

-   Deleting the last track associated with an artist or album may cause information about that artist or album to be lost.

* * *

### SalesFlat

**Merged Tables**

-   InvoiceLine
-   Invoice
-   Customer

**Dependencies**

-   InvoiceLineId → InvoiceId
-   InvoiceId → CustomerId
-   CustomerId → CustomerFirstName, CustomerLastName, Country

**Normal Form Violated**

-   Violates **3NF (Third Normal Form)** because customer information depends on CustomerId rather than directly on the primary key of the flattened table.

**Update Anomaly**

-   If customer information changes, every sales record containing that customer must be updated.
-   Inconsistent updates can result in conflicting customer information.

**Insert Anomaly**

-   A customer cannot be added without creating an invoice or invoice line.
-   Customer information depends on the existence of a sale.

**Delete Anomaly**

-   Deleting a customer's final invoice may remove all information about that customer from the table.

* * *

### CustomerFlat

**Merged Tables**

-   Customer
-   Employee (Support Representative)

**Dependencies**

-   CustomerId → SupportRepId
-   SupportRepId → RepFirstName, RepLastName, RepTitle

**Normal Form Violated**

-   Violates **3NF (Third Normal Form)** because representative information is transitively dependent on CustomerId through SupportRepId.

**Update Anomaly**

-   A support representative's title or name must be updated in every customer record associated with that representative.

**Insert Anomaly**

-   A support representative cannot be stored unless at least one customer is assigned to them.

**Delete Anomaly**

-   Deleting the last customer assigned to a representative may remove all information about that representative from the table.
