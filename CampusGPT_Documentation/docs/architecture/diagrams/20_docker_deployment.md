# Diagram 20 — Docker deployment architecture

**Status:** PROPOSED production layer (WP8); development layer partly EXISTING

```mermaid
flowchart TB
    subgraph Host
        NG["nginx container: 80 and 443"]
        subgraph net["Internal network"]
            BE["backend container, non-root"]
            WK["worker container, PROPOSED"]
            MG["migrate container, one-shot"]
            DBc[("db container: PostgreSQL + pgvector")]
        end
        V1[("volume: pgdata")]
        V2[("volume: uploads")]
    end
    Internet --> NG
    NG -->|"HTTP and WebSocket"| BE
    MG --> DBc
    BE --> DBc
    WK --> DBc
    DBc --- V1
    BE --- V2
    WK --- V2
```

The database port is not published in production; migrate runs before the API starts.
