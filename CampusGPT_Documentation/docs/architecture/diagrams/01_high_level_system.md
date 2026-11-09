# Diagram 01 — High-level system architecture

**Status:** TARGET (PROPOSED); existing-repository parts are PO-RV (previously observed, re-verify)

```mermaid
flowchart LR
    B["Browser: React SPA"] -->|HTTPS| N["Nginx"]
    N -->|static assets| B
    N -->|"/api/v1 HTTP"| A["FastAPI modular monolith"]
    B <-->|"WebSocket"| N
    N <-->|"WebSocket upgrade"| A
    A --> P[("PostgreSQL + pgvector")]
    A --> S[("File storage volume")]
    W["Worker process - same image, PROPOSED"] --> P
    W --> S
    A -->|OTP email| R["Resend"]
    A -->|OAuth| G["Google"]
    A -->|"LLM and embeddings, provider pending PD-11"| L["Configurable provider"]
    A --> BP["BiometricProvider interface - provider pending PD-10"]
    B -->|"Vapi Web SDK"| V["Vapi voice agent"]
    V -->|"custom Function Tool calls"| N
```

Vapi reaches the database only through authenticated FastAPI tool endpoints. See docs 05, 14, 37.
