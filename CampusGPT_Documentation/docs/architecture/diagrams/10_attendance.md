# Diagram 10 — Attendance workflow (face recognition and liveness are required)

**Status:** PROPOSED (P07 slices A and B); provider pending PD-10

```mermaid
flowchart TB
    T["Timetable entry"] --> S["Faculty starts session"]
    S --> O{"Session open"}
    O --> E["Student opens verification"]
    E --> CN{"Consent and enrolment valid"}
    CN -->|no| F["Manual fallback: faculty marks"]
    CN -->|yes| CH["Single-use liveness challenge"]
    CH --> FV["Face match plus liveness via BiometricProvider"]
    GF["Geofence evidence - supporting only"] --> DEC
    FV --> DEC{"Policy decision"}
    DEC -->|accepted| R["Record PRESENT or LATE"]
    DEC -->|rejected or uncertain| NR["NEEDS_REVIEW and fallback signalled"]
    NR --> F
    F --> R
    R --> LV["WebSocket live roster update to faculty"]
    R --> C["Faculty closes session"]
    C --> P["Percentages, shortage and recovery calculated"]
    P --> N["Notification if below threshold"]
    R --> A["Override needs reason - audited, previous value kept"]
```

Duplicate attendance is prevented by a unique (session, student) constraint. Faculty cannot see raw images or templates.
