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
<!-- For each change, name the functional dependency and the normal form it breaks. Example:
"SalesFlat merges Invoice and InvoiceLine. InvoiceDate depends on InvoiceId, not on the key
InvoiceLineId, so this reintroduces a transitive dependency (not 3NF). It saves 3 joins for the
sales-by-country queries." Also list the update, insert, and delete anomalies this creates. -->
