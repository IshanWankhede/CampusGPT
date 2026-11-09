# WebSocket Protocol and Implementation Notes

**Status:** NOT IMPLEMENTED (planned for P12; also used for live attendance in P07). **WebSocket is the intended real-time transport** for the CampusGPT chat experience and live attendance — the owner confirmed the direction (PD-18). Protocol parameters below are the documented proposal pending approval; multi-worker scaling without Redis is PD-25. SSE is not documented as an alternative.

> **Provenance — read before trusting any "existing repository" statement.** Statements about the existing CampusGPT repository come from a read-only audit of an **older snapshot** (`CampusGPT-main.zip`) made earlier in this project. That snapshot is **not** the current live repository, nothing was executed, and no database was touched. All such statements are labelled **PO-RV — Previously observed, re-verification required**. The codebase is the source of truth for what exists; this documentation defines the intended architecture and requirements. Where they disagree, document the discrepancy and request review. Every prompt requires Antigravity to inspect the actual repository before acting; file paths in this package are previously observed paths, not guaranteed ones.

## 1. Endpoints (PROPOSED)
| Path | Purpose | Who |
|---|---|---|
| `/api/v1/ws/chat` | Chat: send messages, stream responses, stop generation | any authenticated user |
| `/api/v1/ws/attendance/{session_id}` | Live roster and verification events | the faculty member who owns the session |
Notifications over WebSocket are a later option (PD-25); until then notifications use normal HTTP polling.

## 2. Connection establishment and authentication
Browsers cannot set an `Authorization` header on a WebSocket, and this project forbids tokens in URLs. Design:
1. Client opens `wss://…/api/v1/ws/chat` (HTTPS/WSS only in production). Server checks the `Origin` header against the allowed list before accepting.
2. Server accepts the upgrade and starts a **5-second authentication timer**.
3. Client's **first message** must be `{"type":"auth","access_token":"…"}`.
4. Server validates the JWT exactly as for HTTP (signature, expiry, `type`, user exists and is active, role from the database). Success → `auth.ok`; failure or timeout → close with code 4401.
5. An alternative (a single-use, 30-second connection ticket obtained over HTTP and passed once) is documented but not preferred because it places a credential in the URL; choose only via an ADR.
6. The connection's identity is fixed at authentication. When the access token expires, the client sends `{"type":"auth.refresh","access_token":"…"}` with a newly refreshed token before expiry; if not renewed in time the server closes with 4401 and the client reconnects.

## 3. Message format
All frames are UTF-8 JSON objects `{"type": "...", "id": "...", ...}`. Maximum frame size 64 KiB (attachments go over HTTP upload, not the socket). Unknown types are rejected with an `error` event.

**Client → server**
| type | Fields | Meaning |
|---|---|---|
| `auth` | `access_token` | first message |
| `auth.refresh` | `access_token` | renew identity |
| `message.create` | `client_message_id`, `conversation_id` (optional for new), `content`, `attachment_ids[]` | send a user message |
| `generation.stop` | `generation_id` | stop the running generation |
| `ping` | — | keep-alive (optional; server also pings) |

**Server → client**
| type | Fields | Meaning |
|---|---|---|
| `auth.ok` | `user_id`, `session_expires_at` | authenticated |
| `conversation.created` | `conversation_id`, `title` | new conversation |
| `generation.started` | `generation_id`, `client_message_id` | typing/generation status begins |
| `status` | `generation_id`, `stage` (`routing`, `retrieving`, `calling_tool`, `generating`) | progress indicator |
| `token.delta` | `generation_id`, `text` | streamed text chunk |
| `source.added` | `generation_id`, `source` (id, title, page/section, link) | citation |
| `generation.completed` | `generation_id`, `message_id`, `usage` | finished and persisted |
| `generation.stopped` | `generation_id`, `message_id` | stopped by the user; partial text persisted |
| `error` | `code`, `message`, `generation_id?`, `retryable` | recoverable or fatal error |
| `pong` | — | keep-alive |

Example flow: `auth` → `auth.ok` → `message.create` → `generation.started` → `status`(routing) → `status`(retrieving) → `source.added`* → `token.delta`* → `generation.completed`.

## 4. Typing and generation status
`generation.started` and `status` drive the "assistant is working" indicator; `token.delta` drives streaming; the UI announces only the completed message to screen readers (not every token).

## 5. Stop generation
Client sends `generation.stop`; server cancels the generation task (LLM request cancelled, tool calls not started), persists the partial text, and replies `generation.stopped`. Disconnecting also cancels any running generation owned by that connection.

## 6. Errors
| Code | Meaning | Retry |
|---|---|---|
| `rate_limited` | per-user budget or frame rate exceeded | after delay |
| `forbidden` | tool/resource not permitted | no |
| `provider_unavailable` | LLM/embedding provider failure | yes |
| `invalid_message` | schema or size violation | no |
| `internal` | unexpected error (generic text only) | maybe |
Close codes: 4401 not authenticated / auth timeout, 4403 forbidden, 4408 idle timeout, 4413 message too large, 4429 too many connections or messages, 1011 server error, 1001 going away (deploy).

## 7. Reconnection behaviour
- Client reconnects with exponential backoff and jitter (1 s, 2 s, 4 s … capped at 30 s), refreshing the access token first (through `apiFetch`, WP7).
- After reconnecting the client loads the conversation history over HTTP (`GET /api/v1/ai/conversations/{id}/messages`) and shows any completed message it missed; an interrupted generation is shown as interrupted and the user can regenerate. `client_message_id` makes `message.create` idempotent so a retry does not duplicate the user message.
- No in-socket replay buffer in the first release (keeps the server stateless per connection; revisit under PD-25).
- UI states: connecting, connected, reconnecting (with the message input still usable offline-queued only if the owner approves), disconnected.

## 8. Authorisation
Connection identity is the authenticated user. Every `message.create` runs the normal pipeline (intent routing → permission-checked tools/RAG). Conversation ids are checked for ownership on every message. The attendance channel verifies the caller owns the session on connect and rejects subscriptions to other sessions. Nothing received over the socket is trusted for identity or role.

## 9. Limits
Per-user concurrent connections (default 3), idle timeout 60 s without ping/pong, server ping every 20 s, one active generation per conversation, message rate limit, 64 KiB frames, maximum message length, token budgets per user/day. Limits are configuration values.

## 10. Connection cleanup
On close or error: cancel running tasks, release the connection from the in-process registry, flush partial output, write usage and audit entries, never leave orphaned provider requests.

## 11. FastAPI implementation notes (PROPOSED)
- Routers in the `ai` and `attendance` modules declare `@router.websocket(...)` endpoints; a small connection-manager object holds the per-process registry keyed by user and connection.
- Authentication is a shared helper that reuses the existing JWT verification code; authorisation reuses the same policy functions as HTTP routes.
- Generation runs as a cancellable `asyncio` task so receiving frames (e.g. `generation.stop`) is never blocked; outgoing writes use bounded queues to apply back-pressure to slow clients.
- Blocking work (database, parsing) runs in the thread pool or async drivers according to the established convention in the repository — **verify the repository's sync/async style before implementing**.
- Run the application with a WebSocket-capable ASGI server (uvicorn with a WebSocket library installed — verify the installed set).

## 12. Nginx configuration (PROPOSED)
```nginx
location /api/v1/ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 120s;
    proxy_send_timeout 120s;
    proxy_buffering off;
}
```
Forwarded headers are trusted only from Nginx (same trust list as rate limiting, WP5). The service name `backend` and port are previously observed — verify.

## 13. Frontend connection handling (PROPOSED)
A `useChatSocket` hook in the AI feature owns the socket: state machine (connecting → authenticating → ready → reconnecting → closed), automatic reconnect with backoff, token refresh through `apiFetch`, event dispatch to the chat store, cleanup on unmount, and a text-mode fallback if the socket cannot be established (the HTTP history endpoint still works). It never logs tokens or message contents.

## 14. Scaling and the no-Redis rule
Connections live in a single backend process. Chat needs no cross-connection broadcast, so it works with several workers as long as each connection stays on one worker. Live attendance and future notification pushes **do** need delivery to the right connection; options are a single worker initially, HTTP polling fallback, or PostgreSQL LISTEN/NOTIFY fan-out. **Redis is not added.** The choice is recorded as a decision requiring approval (PD-25) instead of being decided silently.

## 15. Testing
Authentication timeout and failure; expired token; user identity fixed per connection; cross-user conversation id rejected; stop generation; disconnect cancels generation; reconnect with idempotent `client_message_id`; oversize frame; rate limit; Origin rejection; attendance channel rejects other faculty; Nginx upgrade through the production proxy in staging.

## 16. Acceptance criteria
- [ ] Protocol implemented as documented, or deviations recorded in an ADR.
- [ ] No token in any URL or log.
- [ ] Stop, errors, reconnection and cleanup tested.
- [ ] Nginx WebSocket proxying verified.
- [ ] PD-18 parameters approved; PD-25 decision recorded before multi-worker deployment.
