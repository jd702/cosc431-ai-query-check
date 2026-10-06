1. What are the titles of all albums by the artist 'AC/DC'?

SELECT Album.Title
FROM Artist
JOIN Album ON Artist.ArtistId = Album.ArtistId
WHERE Artist.Name = 'AC/DC';

πTitle (σName=′AC/DC′(Artist⋈Album))

Both SQL and relational algebra use selection to find the artist AC/DC and projection to return the album titles. 
SQL uses SELECT, WHERE, and JOIN, while relational algebra uses π, σ, and ⋈ to perform the same operations.

2. What are the invoice dates for customers with the first name Astrid and the last name Gruber?

SELECT Invoice.InvoiceDate
FROM Customer
JOIN Invoice ON Customer.CustomerId = Invoice.CustomerId
WHERE Customer.FirstName = 'Astrid'
  AND Customer.LastName = 'Gruber';

πInvoiceDate (σFirstName=′Astrid′∧LastName=′Gruber′(Customer⋈Invoice))

Both versions filter customers by first and last name, join the Customer and Invoice tables, and return the invoice dates. 
SQL uses WHERE and JOIN, while relational algebra uses selection (σ), projection (π), and a join (⋈).

3. Count the number of tracks that are of the media type 'AAC audio file'.

SELECT COUNT(Track.TrackId) AS TrackCount
FROM MediaType
JOIN Track ON MediaType.MediaTypeId = Track.MediaTypeId
WHERE MediaType.Name = 'AAC audio file';

γCOUNT(TrackId)→TrackCount (σName=′AACaudiofile′ (MediaType⋈Track))

Both versions identify tracks with the media type AAC audio file and count them. 
SQL uses COUNT() and WHERE, while relational algebra uses the aggregate operator γ and selection (σ).

4. Which artist has the most albums?

SELECT Artist.Name, COUNT(Album.AlbumId) AS AlbumCount
FROM Artist
JOIN Album ON Artist.ArtistId = Album.ArtistId
GROUP BY Artist.ArtistId, Artist.Name
ORDER BY AlbumCount DESC
LIMIT 1;

A←γ ArtistId,Name;COUNT(AlbumId)→AlbumCount (Artist⋈Album)
πName(σAlbumCount=MaxCount(A×γMAX(AlbumCount)→MaxCount(A)))

Both versions count the albums associated with each artist and identify the artist with the highest count. 
SQL uses GROUP BY, COUNT(), and a comparison with the maximum count, while relational algebra uses 
grouping and aggregation (γ), along with selection (σ), to identify the artist.

5. How many albums are there?

SELECT COUNT(AlbumId) AS AlbumCount
FROM Album;

γCOUNT(AlbumId)→AlbumCount (Album)

Both versions calculate the total number of albums in the database. SQL uses COUNT() to count the album records, 
while relational algebra uses the aggregation operator γ with COUNT() to produce the same result.