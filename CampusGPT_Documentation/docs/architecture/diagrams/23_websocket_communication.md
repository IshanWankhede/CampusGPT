# Diagram 23 — WebSocket communication flow

**Status:** PROPOSED (P12; live attendance P07); PD-18 parameters, PD-25 scaling

```mermaid
sequenceDiagram
    participant FE as React useChatSocket
    participant N as Nginx
    participant WS as FastAPI WebSocket
    participant AI as Orchestrator
    FE->>N: Upgrade to /api/v1/ws/chat
    N->>WS: Upgrade, Origin checked
    FE->>WS: auth message with access token
    WS->>WS: Validate JWT within 5 seconds
    WS-->>FE: auth.ok
    FE->>WS: message.create with client_message_id
    WS-->>FE: generation.started
    WS->>AI: Run pipeline with caller identity
    AI-->>WS: status, sources, text deltas
    WS-->>FE: status, source.added, token.delta
    opt user presses stop
        FE->>WS: generation.stop
        WS->>AI: Cancel task
        WS-->>FE: generation.stopped
    end
    AI-->>WS: Completed and persisted
    WS-->>FE: generation.completed
    Note over FE,WS: On drop the client refreshes its token, reconnects with backoff and reloads history over HTTP
```

WebSocket is the only real-time transport; no Redis. See `docs/architecture/WebSocket_Protocol.md`.
