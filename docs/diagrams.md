# Diagrams

GitHub renders these Mermaid blocks automatically. For slides later, screenshot them from the
rendered page, or paste a block into mermaid.live to export a PNG.

## 1. ER diagram — normalized Chinook (3NF)

Row counts are from our local build. Crow's-foot notation: `||--o{` is one-to-many.

```mermaid
erDiagram
    ARTIST     ||--o{ ALBUM        : "records"
    ALBUM      ||--o{ TRACK        : "contains"
    GENRE      ||--o{ TRACK        : "classifies"
    MEDIATYPE  ||--o{ TRACK        : "encodes"
    TRACK      ||--o{ INVOICELINE  : "is sold as"
    TRACK      ||--o{ PLAYLISTTRACK : "appears in"
    PLAYLIST   ||--o{ PLAYLISTTRACK : "groups"
    INVOICE    ||--o{ INVOICELINE  : "itemizes"
    CUSTOMER   ||--o{ INVOICE      : "is billed"
    EMPLOYEE   ||--o{ CUSTOMER     : "supports"
    EMPLOYEE   ||--o{ EMPLOYEE     : "reports to"

    ARTIST {
        int ArtistId PK "275 rows"
        nvarchar Name
    }
    ALBUM {
        int AlbumId PK "347 rows"
        nvarchar Title
        int ArtistId FK
    }
    TRACK {
        int TrackId PK "3503 rows"
        nvarchar Name
        int AlbumId FK "nullable"
        int MediaTypeId FK
        int GenreId FK "nullable"
        nvarchar Composer
        int Milliseconds
        numeric UnitPrice
    }
    GENRE {
        int GenreId PK "25 rows"
        nvarchar Name
    }
    MEDIATYPE {
        int MediaTypeId PK "5 rows"
        nvarchar Name
    }
    PLAYLIST {
        int PlaylistId PK "18 rows"
        nvarchar Name
    }
    PLAYLISTTRACK {
        int PlaylistId PK_FK "8715 rows"
        int TrackId PK_FK
    }
    CUSTOMER {
        int CustomerId PK "59 rows"
        nvarchar FirstName
        nvarchar LastName
        nvarchar Address
        nvarchar Country
        nvarchar Email
        int SupportRepId FK "nullable"
    }
    EMPLOYEE {
        int EmployeeId PK "8 rows"
        nvarchar FirstName
        nvarchar LastName
        nvarchar Title
        int ReportsTo FK "nullable"
    }
    INVOICE {
        int InvoiceId PK "412 rows"
        int CustomerId FK
        datetime InvoiceDate
        nvarchar BillingCity
        nvarchar BillingCountry
        numeric Total
    }
    INVOICELINE {
        int InvoiceLineId PK "2240 rows"
        int InvoiceId FK
        int TrackId FK
        numeric UnitPrice
        int Quantity
    }
```

## 2. Denormalized variant — what collapses into what

Each flat table absorbs the tables on its left, removing joins at the cost of 3NF violations
(details in [deliverable1_writeup.md](deliverable1_writeup.md)).

```mermaid
flowchart LR
    subgraph N["Normalized (3NF)"]
        AR[Artist] --> AL[Album]
        AL --> TR[Track]
        GE[Genre] --> TR
        MT[MediaType] --> TR
        TR --> IL[InvoiceLine]
        IN[Invoice] --> IL
        CU[Customer] --> IN
        EM[Employee] --> CU
    end

    subgraph D["Denormalized (read-optimized)"]
        TF["TrackFlat<br/>3,503 rows<br/>breaks 3NF"]
        SF["SalesFlat<br/>2,240 rows<br/>breaks 3NF"]
        CF["CustomerFlat<br/>59 rows<br/>breaks 3NF"]
    end

    TR -.-> TF
    AL -.-> TF
    AR -.-> TF
    GE -.-> TF
    MT -.-> TF
    IL -.-> SF
    IN -.-> SF
    CU -.-> SF
    CU -.-> CF
    EM -.-> CF
```

| Flat table | Joins removed | Benchmark questions served |
|---|---|---|
| `TrackFlat` | 4 | Q09, Q10, Q13, Q14, Q15, Q20 |
| `SalesFlat` | 3 | Q02, Q07, timing queries |
| `CustomerFlat` | 1 | Q11, Q12, Q16 |

## 3. Evaluation pipeline — how the benchmark runs

This is the architecture of the experiment: one prompt, two models, three graded dimensions.

```mermaid
flowchart TD
    SP["Spider benchmark<br/>(chinook_1)"] --> QS["questions.json<br/>20 questions + gold SQL"]
    DDL["normalized_schema.sql<br/>CREATE TABLE statements"] --> PR

    QS --> PR["Prompt = schema + question<br/>'return only SQL'"]
    PR --> GEM["Gemini<br/>gemini-2.5-flash-lite"]
    PR --> LLA["Llama via Groq<br/>llama-3.1-8b-instant"]

    GEM --> GEN["generated_sql.json<br/>1 run per question per model"]
    LLA --> GEN

    QS --> GR["gold_results.json<br/>verified result sets"]
    DB[("chinook.db<br/>normalized")] --> GR

    GEN --> EXEC["Execute each generated query"]
    DB --> EXEC
    EXEC --> C1["1. Correctness<br/>compare RESULT SETS, not SQL text"]
    GR --> C1

    GEN --> C2["2. Security audit<br/>auto pre-screen + manual review"]
    CL["security_checklist.md<br/>stacked ; / OR 1=1 / -- / UNION"] --> C2

    BQ["benchmark_queries.json"] --> C3["3. Performance<br/>4 conditions, timeit"]
    DB --> C3
    DB2[("chinook_denorm.db<br/>+ flat tables")] --> C3

    C1 --> RPT["Report + presentation"]
    C2 --> RPT
    C3 --> RPT
```

## 4. The four performance conditions

```mermaid
flowchart LR
    Q["Benchmark query<br/>(join or WHERE on non-key)"] --> A["Normalized<br/>no index"]
    Q --> B["Normalized<br/>+ index"]
    Q --> C["Denormalized<br/>no index"]
    Q --> D["Denormalized<br/>+ index"]
    A --> T["timeit: best-of-5,<br/>20 executions each"]
    B --> T
    C --> T
    D --> T
    T --> P["performance.csv<br/>+ EXPLAIN QUERY PLAN"]
```

Note: Chinook ships 11 of its own `IFK_*` foreign-key indexes, so the "no index" conditions must
drop those first or the baseline is already indexed.
