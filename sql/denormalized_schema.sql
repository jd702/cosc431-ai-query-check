-- Denormalized variant of Chinook (Deliverable 1, Step 5)
--
-- Applied on top of the normalized Chinook tables in data/chinook_denorm.db, so the
-- same gold queries can run against both databases. Each flat table below collapses a
-- join path that our 20 benchmark questions use repeatedly.
--
-- Nullable foreign keys (Track.AlbumId, Track.GenreId) are flattened with LEFT JOIN so
-- no rows are silently lost. The current data has no NULLs in those columns, but the
-- schema permits them, and an INNER JOIN here would make the denormalized copy return
-- different results from the normalized one.
--
-- See docs/deliverable1_writeup.md for the dependencies, normal forms and anomalies.

-- 1. TrackFlat: Track + Album + Artist + Genre + MediaType
--    Serves Q09, Q10, Q13, Q14, Q15, Q20 (currently 2-4 joins each).
--    Key: TrackId. Breaks 3NF: TrackId -> AlbumId -> AlbumTitle, ArtistId -> ArtistName.
DROP TABLE IF EXISTS TrackFlat;
CREATE TABLE TrackFlat AS
SELECT
    t.TrackId,
    t.Name          AS TrackName,
    t.Composer,
    t.Milliseconds,
    t.Bytes,
    t.UnitPrice,
    al.AlbumId,
    al.Title        AS AlbumTitle,
    ar.ArtistId,
    ar.Name         AS ArtistName,
    g.GenreId,
    g.Name          AS GenreName,
    m.MediaTypeId,
    m.Name          AS MediaTypeName
FROM Track t
LEFT JOIN Album     al ON al.AlbumId     = t.AlbumId
LEFT JOIN Artist    ar ON ar.ArtistId    = al.ArtistId
LEFT JOIN Genre     g  ON g.GenreId      = t.GenreId
LEFT JOIN MediaType m  ON m.MediaTypeId  = t.MediaTypeId;

-- 2. SalesFlat: InvoiceLine + Invoice + Customer + Track
--    Serves the sales/customer questions (Q02, Q07) and the D2 timing queries.
--    Key: InvoiceLineId. Breaks 2NF/3NF: InvoiceLineId -> InvoiceId -> InvoiceDate,
--    BillingCountry, CustomerId; CustomerId -> customer name and country.
DROP TABLE IF EXISTS SalesFlat;
CREATE TABLE SalesFlat AS
SELECT
    il.InvoiceLineId,
    i.InvoiceId,
    i.InvoiceDate,
    i.BillingCity,
    i.BillingCountry,
    i.Total           AS InvoiceTotal,
    c.CustomerId,
    c.FirstName       AS CustomerFirstName,
    c.LastName        AS CustomerLastName,
    c.Address         AS CustomerAddress,
    c.Country         AS CustomerCountry,
    c.SupportRepId,
    t.TrackId,
    t.Name            AS TrackName,
    t.GenreId,
    il.UnitPrice,
    il.Quantity
FROM InvoiceLine il
JOIN Invoice  i ON i.InvoiceId  = il.InvoiceId
JOIN Customer c ON c.CustomerId = i.CustomerId
JOIN Track    t ON t.TrackId    = il.TrackId;

-- 3. CustomerFlat: Customer + their support representative
--    Serves Q11, Q12, Q16 without the Customer-Employee join.
--    Key: CustomerId. Breaks 3NF: CustomerId -> SupportRepId -> rep name and title.
DROP TABLE IF EXISTS CustomerFlat;
CREATE TABLE CustomerFlat AS
SELECT
    c.CustomerId,
    c.FirstName     AS CustomerFirstName,
    c.LastName      AS CustomerLastName,
    c.Country       AS CustomerCountry,
    c.Email,
    c.SupportRepId,
    e.FirstName     AS RepFirstName,
    e.LastName      AS RepLastName,
    e.Title         AS RepTitle
FROM Customer c
LEFT JOIN Employee e ON e.EmployeeId = c.SupportRepId;
