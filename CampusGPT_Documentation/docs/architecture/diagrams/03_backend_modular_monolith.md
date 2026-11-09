# Diagram 03 — Backend modular monolith

**Status:** EXISTING: auth module only; others PROPOSED

```mermaid
flowchart TB
    R["main.py: routers, middleware"] --> AU["auth - EXISTING"]
    R --> ADM["admin - PROPOSED"]
    R --> ERP["students, faculty, attendance, timetable, assignments, notices - PROPOSED"]
    R --> DOC["documents - PROPOSED"]
    R --> AIM["ai: orchestrator, routing, tools - PROPOSED"]
    R --> RAG["rag - PROPOSED"]
    R --> AN["analytics, placements, opportunities, courses, visual - PROPOSED"]
    AU --> POL["policies: shared permission functions"]
    ERP --> POL
    DOC --> POL
    AIM --> POL
    RAG --> POL
    POL --> REPO["repositories - SQLAlchemy"]
    REPO --> DB[("PostgreSQL")]
    CORE["core: config, dependencies, logging, audit"] --- R
```

Every module calls permission functions in one place; AI tools use the same policies as HTTP routes.
