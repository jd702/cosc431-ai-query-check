-- Denormalized variant of Chinook (Deliverable 1, Step 5)
-- OWNER: Schema lead. This is a STARTER example — revise it and document every
-- change in docs/deliverable1_writeup.md in normalization terms.
--
-- Example 1: SalesFlat merges Invoice + InvoiceLine + Customer + Track.
--   InvoiceLine's key is InvoiceLineId, but InvoiceDate, BillingCountry and the
--   customer columns depend only on InvoiceId / CustomerId -> transitive
--   dependencies are reintroduced (violates 3NF). Saves 2–3 joins for sales queries.
--
-- Example 2: TrackFlat merges Track + Album + Artist + Genre + MediaType.
--   ArtistName depends on AlbumId, not TrackId -> transitive dependency (violates 3NF).
--
-- The normalized tables are still present in chinook_denorm.db so the same gold
-- queries run on both; the timing notebook uses rewritten queries against these
-- flat tables for the denormalized conditions.

DROP TABLE IF EXISTS SalesFlat;
CREATE TABLE SalesFlat AS
SELECT
    il.InvoiceLineId,
    i.InvoiceId,
    i.InvoiceDate,
    i.BillingCity,
    i.BillingCountry,
    i.Total          AS InvoiceTotal,
    c.CustomerId,
    c.FirstName      AS CustomerFirstName,
    c.LastName       AS CustomerLastName,
    c.Country        AS CustomerCountry,
    c.SupportRepId,
    t.TrackId,
    t.Name           AS TrackName,
    t.GenreId,
    il.UnitPrice,
    il.Quantity
FROM InvoiceLine il
JOIN Invoice  i ON i.InvoiceId  = il.InvoiceId
JOIN Customer c ON c.CustomerId = i.CustomerId
JOIN Track    t ON t.TrackId    = il.TrackId;

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
JOIN Album     al ON al.AlbumId    = t.AlbumId
JOIN Artist    ar ON ar.ArtistId   = al.ArtistId
LEFT JOIN Genre g ON g.GenreId     = t.GenreId
JOIN MediaType m  ON m.MediaTypeId = t.MediaTypeId;
