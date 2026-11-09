# Diagram 24 — Face recognition and liveness workflow

**Status:** PROPOSED (P07 slice B); provider pending PD-10

```mermaid
flowchart TB
    A["Student opens verification for an open session"] --> B{"Valid consent"}
    B -->|no| M["Manual fallback"]
    B -->|yes| C{"Enrolled template exists"}
    C -->|no| EN["Enrolment flow with consent"]
    C -->|yes| D["Server issues single-use liveness challenge"]
    D --> E["Camera capture and prompts"]
    E --> F["Liveness checks: challenge-response, presentation-attack detection, blink as one signal"]
    F -->|fail| NR["Event stored, NEEDS_REVIEW"]
    F -->|pass| G["Match against enrolled template"]
    G --> H["Add geofence evidence - supporting only"]
    H --> I{"Policy thresholds"}
    I -->|accept| J["Attendance recorded, live roster updated"]
    I -->|reject or uncertain| NR
    NR --> M
    M --> K["Faculty marks or overrides with reason, audited"]
    E --> X["Raw frames deleted after processing"]
```

No component of this workflow guarantees protection against every spoofing attack; manual review and audit remain (doc 14).
