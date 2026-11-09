# Diagram 19 — Vapi voice architecture

**Status:** PROPOSED (P22); deployment details PD-19

```mermaid
flowchart LR
    U["User with microphone"] --> FE["React voice screen"]
    FE -->|"1 create voice session with JWT"| API["FastAPI voice module"]
    API -->|"short-lived voice session"| FE
    FE -->|"Vapi Web SDK - public key"| V["Vapi voice agent: STT, LLM, TTS"]
    V -->|"custom Function Tool call"| T["FastAPI tool endpoint"]
    T --> AZ["Vapi server auth + voice-session binding + policies"]
    AZ --> SVC["Existing services and RAG"]
    SVC --> DB[("PostgreSQL + pgvector")]
    T -->|"minimal permitted result"| V
    V -->|speech| FE
    FE -.->|fallback| CH["Text chat over WebSocket"]
```

```mermaid
sequenceDiagram
    participant V as Vapi agent
    participant T as FastAPI tool endpoint
    participant S as Voice session store
    participant P as Policies and services
    V->>T: Tool call with Vapi credential and call identifiers
    T->>T: Verify request is from Vapi
    T->>S: Resolve active voice session and bound user
    S-->>T: user id and scope
    T->>P: Validate arguments, apply policy for that user
    P-->>T: Minimal permitted data
    T-->>V: Result
```

Vapi has no database access; user identity is derived from the voice session, never from model-supplied arguments (doc 37).
