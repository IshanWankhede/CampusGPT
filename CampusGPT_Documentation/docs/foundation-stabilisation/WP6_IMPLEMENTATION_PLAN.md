# WP6 — Refresh Token Rotation and Revocation: Implementation Plan

**Stage 0 Foundation Work Package — Step 12**  
**Status:** Planning (Revision 1) — Awaiting Approval  
**Target Migration:** `0011_create_refresh_tokens_table.py` (down-revision: `0010`)  
**Database Target:** Strictly `campusgpt_test` (Original `campusgpt` DB untouched at revision `0005`)  

---

## 1. Baseline Inspection & Verification Findings

### 1.1 Existing Token Lifecycle Audit
- **Issuance Points:** Tokens are issued in two places:
  1. `POST /api/v1/auth/login` (calls `service.create_access_token` and `service.create_refresh_token`).
  2. `POST /api/v1/auth/google/exchange` (WP4 endpoint; issues access and refresh tokens).
- **Current Refresh Endpoint (`POST /api/v1/auth/refresh`):**
  - Accepts `RefreshRequest(refresh_token: str)`.
  - Verifies stateless JWT signature via `service.decode_token(..., "refresh")`.
  - Returns only `AccessTokenResponse(access_token=...)`.
  - **Defect:** Does not rotate the refresh token, does not track tokens server-side, and does not detect stolen/reused refresh tokens.
- **Current Logout Endpoint (`POST /api/v1/auth/logout`):**
  - Takes `current_user: Annotated[User, Depends(get_current_user)]`.
  - Returns `204 No Content` without revoking anything server-side.
- **Current Dependency (`get_current_user` in `backend/app/core/dependencies.py`):**
  - Decodes `access` JWT, extracts `user_id`.
  - Executes `user = repository.get_user_by_id(db, user_id)`.
  - Checks `if user is None or not user.is_active: raise 401`.
  - **Confirmed:** Re-reads the live database user record and role on every authenticated request.
- **Current Frontend (`frontend/src/context/AuthContext.jsx`):**
  - Tokens stored in `localStorage` under key `campusgpt.auth`.
  - Does **not** intercept 401s or call `/refresh`.
  - `logout()` sends no body and only clears `localStorage`.
- **Database Status:**
  - `campusgpt` (original dev DB): Revision `0005`, 4 users, 11 OTPs (**untouched**).
  - `campusgpt_test`: Revision `0010` (includes WP1 `users`, WP2 `role_requests`, WP4 `login_codes`, WP5 `auth_attempts`).
  - Total test suite: 121/121 passing.

---

## 2. Database Architecture & Additive Migration (Revision 0011)

### 2.1 Table Schema: `refresh_tokens`
We store token identifiers (`jti`) and family tracking metadata, **never raw JWTs**:

```sql
CREATE TABLE refresh_tokens (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jti          UUID NOT NULL UNIQUE,          -- Token ID embedded in JWT 'jti' claim
    family_id    UUID NOT NULL,                 -- Preserved across rotations within a session
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at   TIMESTAMPTZ NOT NULL,          -- 7 days from creation
    revoked_at   TIMESTAMPTZ,                   -- NULL while active; timestamp when rotated/revoked
    replaced_by  UUID,                          -- jti of the child token that rotated this one
    user_agent   VARCHAR(256),
    ip_hash      VARCHAR(64),                   -- SHA-256 of client IP (WP5 hash_ip helper)
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_refresh_tokens_jti ON refresh_tokens (jti);
CREATE INDEX ix_refresh_tokens_family_id ON refresh_tokens (family_id);
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX ix_refresh_tokens_active_lookup ON refresh_tokens (jti, revoked_at, expires_at);
```

### 2.2 Model Definition (`backend/app/models/refresh_token.py`)
```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_tokens_family_id", "family_id"),
        Index("ix_refresh_tokens_user_id", "user_id"),
        Index("ix_refresh_tokens_active_lookup", "jti", "revoked_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False)
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
```

Export `RefreshToken` in `backend/app/models/__init__.py`.

---

## 3. Token Architecture & Rotation Strategy

### 3.1 Claims Structure
- **Access Token (15-minute lifetime, PD-03):**
  - `sub`: `str(user.id)`
  - `role`: `user.role.value`
  - `type`: `"access"`
  - `iat`: current UTC timestamp
  - `exp`: `iat + 15 minutes` (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES = 15`)
- **Refresh Token (7-day lifetime):**
  - `sub`: `str(user.id)`
  - `jti`: `str(uuid.UUID)` (unique token ID)
  - `family_id`: `str(uuid.UUID)` (session family ID)
  - `type`: `"refresh"`
  - `iat`: current UTC timestamp
  - `exp`: `iat + 7 days` (configurable via `REFRESH_TOKEN_EXPIRE_DAYS = 7`)

### 3.2 Rotation Algorithm (`rotate_refresh_token`)
When `POST /api/v1/auth/refresh` is called:
1. Decode and validate the refresh JWT signature and expiry. Extract `sub`, `jti`, `family_id`.
2. Parse `jti` and `family_id` as UUIDs. If missing or malformed, raise `401 Unauthorized` ("Invalid refresh token").
3. In a transaction with PostgreSQL row locking (`SELECT ... FOR UPDATE` on `refresh_tokens WHERE jti = :jti`):
   - **Case A: Token not found in database:**
     - Reject with `401 Unauthorized` ("Invalid refresh token"). (Stateless legacy tokens without DB entries are immediately invalidated).
   - **Case B: Token already revoked (`revoked_at IS NOT NULL`):**
     - Check elapsed time since revocation: `elapsed = (now - token.revoked_at).total_seconds()`.
     - **Leeway check (`elapsed <= 10.0` seconds):**
       - Tolerate benign race conditions (e.g. two browser tabs firing refresh within seconds of each other).
       - Reject this specific request with `401 Unauthorized` (`detail="Refresh token already rotated. Please use the newest token."`), but **do not** revoke the token family.
     - **Compromise detected (`elapsed > 10.0` seconds):**
       - A previously rotated token was reused outside the grace period — token theft has occurred!
       - **Revoke the entire family:**
         `UPDATE refresh_tokens SET revoked_at = now WHERE family_id = :family_id AND revoked_at IS NULL`.
       - Raise `401 Unauthorized` (`detail="Compromised refresh token reuse detected. All sessions in this family have been terminated."`).
   - **Case C: Token expired (`expires_at <= now`):**
     - Mark `revoked_at = now`.
     - Reject with `401 Unauthorized` (`detail="Refresh token expired"`).
   - **Case D: User deactivated (`user.is_active is False`):**
     - Revoke token and reject with `401 Unauthorized` (`detail="User account deactivated"`).
   - **Case E: Valid active token (`revoked_at IS NULL` and `expires_at > now`):**
     - Generate `new_jti = uuid.uuid4()`.
     - Mark current token rotated:
       - `token.revoked_at = now`
       - `token.replaced_by = new_jti`
     - Insert new active `RefreshToken` record:
       - `jti = new_jti`
       - `family_id = token.family_id` (preserves the family)
       - `user_id = token.user_id`
       - `issued_at = now`
       - `expires_at = now + 7 days`
       - `user_agent = request.headers.get("user-agent")[:256]`
       - `ip_hash = hash_ip(client_ip)`
     - Issue newly minted access token and newly minted rotated refresh token.
     - Commit transaction atomically.
     - Return `TokenResponse(access_token=..., refresh_token=..., token_type="bearer", user=...)`.

---

## 4. API Endpoints & Contract Changes

### 4.1 Modified: `POST /api/v1/auth/refresh`
- **Request Body:** `RefreshRequest(refresh_token: str)`
- **Response Model:** `TokenResponse` (returns rotated `access_token` AND rotated `refresh_token`).
- **Status:** 200 OK on rotation; 401 on invalid/revoked/compromised/expired token.

### 4.2 Modified: `POST /api/v1/auth/logout`
- **Request Body:** `LogoutRequest(refresh_token: str | None = None)`
- **Headers:** Optional `Authorization: Bearer <access_token>`
- **Behavior:**
  - If `refresh_token` provided, decodes `jti` and revokes that token and its immediate family:
    `UPDATE refresh_tokens SET revoked_at = now WHERE family_id = :family_id AND revoked_at IS NULL`.
  - If only `access_token` provided, revokes the user's most recent active session.
  - Returns `204 No Content`.

### 4.3 New: `POST /api/v1/auth/logout-all`
- **Auth:** Requires `current_user: Annotated[User, Depends(get_current_user)]`
- **Behavior:**
  - Revokes all active refresh tokens for the authenticated user across all devices:
    `UPDATE refresh_tokens SET revoked_at = now WHERE user_id = :user_id AND revoked_at IS NULL`.
  - Returns `204 No Content`.

### 4.4 Cascading Revocations
- **Password Reset (`reset-password` endpoint):**
  - When password is changed, execute:
    `UPDATE refresh_tokens SET revoked_at = now WHERE user_id = :user_id AND revoked_at IS NULL`.
  - Immediately logs out all active sessions on other devices.
- **Role Request Approval (`manage_role_requests.py`):**
  - When an admin approves or updates a user's role, revoke active refresh tokens so the next token issuance immediately reflects the new role claims.

---

## 5. Frontend Integration (`AuthContext.jsx`)

### 5.1 Automatic Refresh on HTTP 401
Enhance `request(path, options)` with automatic 401 retry:
1. If a network request receives `401 Unauthorized` and is **not** an auth route (`/login`, `/refresh`, `/register`):
2. Check if a retry has already been attempted on this request (`options._retry`). If `options._retry === true`, do not retry — immediately fail to prevent infinite loops.
3. Check if stored `session?.refresh_token` exists:
   - If missing: clear storage and set `session = null`.
4. **Single-Flight Concurrency Guard (Refresh Mutex):**
   - If multiple parallel API calls receive 401 simultaneously (e.g. page load with dashboard data), they must not trigger multiple concurrent `/refresh` requests.
   - Maintain a module-level `refreshPromise`:
     ```javascript
     let refreshPromise = null;

     async function getRefreshedToken(refreshToken) {
       if (!refreshPromise) {
         refreshPromise = fetch("/api/v1/auth/refresh", {
           method: "POST",
           headers: { "Content-Type": "application/json" },
           body: JSON.stringify({ refresh_token: refreshToken }),
         })
           .then(async (res) => {
             if (!res.ok) throw new Error("Refresh failed");
             return res.json();
           })
           .finally(() => {
             refreshPromise = null;
           });
       }
       return refreshPromise;
     }
     ```
   - All awaiting requests receive the updated `access_token`.
   - Update `localStorage` with rotated `{ access_token, refresh_token, user }`.
   - Replay original request with updated `Authorization: Bearer ${new_access_token}` and `_retry: true`.
   - If `getRefreshedToken` fails: clear `localStorage`, clear session state, redirect to `/auth`.

### 5.2 Updated Logout
- `logout()` sends `session.refresh_token` in body to `POST /api/v1/auth/logout`.
- Clears `localStorage` regardless of network response.

---

## 6. Security Considerations & Storage Documentation (PD-04, PD-23)

1. **Storage Trade-offs:**
   - In current architecture, tokens reside in `localStorage`.
   - *Limitation:* `localStorage` is vulnerable to extraction via Cross-Site Scripting (XSS).
   - *Mitigation in WP6:* Access tokens are short-lived (15 minutes). Refresh tokens are rotated on every use with strict reuse detection and family revocation. If an attacker steals a refresh token and uses it, the legitimate user's subsequent use triggers family revocation, terminating the attacker's session.
   - *Production Option:* Document migration path to HttpOnly, SameSite=Lax/Strict cookies for refresh tokens in production deployments.
2. **Deterministic Concurrency:**
   - Database operations use PostgreSQL row locking (`FOR UPDATE`) or atomic `UPDATE ... WHERE revoked_at IS NULL` to ensure race conditions are resolved cleanly at the database level.

---

## 7. Comprehensive Test Plan (`backend/tests/test_refresh_token_wp6.py`)

A dedicated suite of 14 deterministic tests:

1. `test_login_issues_tracked_refresh_token_with_jti`: Verify DB row created with `jti`, `family_id`, and active status.
2. `test_refresh_happy_path_rotates_tokens`: Verify `/refresh` returns new access + new refresh token, marks old row revoked with `replaced_by`, and creates new active row with same `family_id`.
3. `test_old_refresh_token_fails_after_rotation`: Using the old refresh token after rotation fails with 401.
4. `test_refresh_token_reuse_outside_leeway_revokes_entire_family`: Presenting a revoked token after 10s revokes all tokens in the family; new token in family also becomes invalid.
5. `test_refresh_token_reuse_inside_leeway_window_tolerates_race`: Presenting a revoked token within 10s is rejected but does NOT revoke the family.
6. `test_concurrent_refresh_calls_exactly_one_succeeds`: Two concurrent threads calling `/refresh` with the same token: exactly 1 succeeds, 1 receives 401.
7. `test_logout_revokes_token_family`: Calling `/logout` with refresh token revokes the family.
8. `test_logout_all_revokes_all_user_tokens`: Calling `/logout-all` revokes all active tokens across multiple families for that user.
9. `test_password_reset_revokes_all_refresh_tokens`: Resetting password immediately revokes all active refresh tokens for the user.
10. `test_deactivated_user_cannot_refresh`: An inactive user (`is_active=False`) receives 401 on `/refresh`.
11. `test_expired_refresh_token_rejected`: A token past its 7-day expiry receives 401 and is marked revoked.
12. `test_stateless_legacy_token_rejected`: A JWT without a matching database `jti` row receives 401.
13. `test_access_token_configured_to_15_minutes`: Assert decoded access token expiration is 15 minutes from `iat`.
14. `test_google_oauth_exchange_issues_tracked_refresh_token`: Verify WP4 `/google/exchange` produces a tracked refresh token with `family_id`.

---

## 8. Implementation Steps & Sequencing

1. **Step 1:** Create `backend/app/models/refresh_token.py` and register in `backend/app/models/__init__.py`.
2. **Step 2:** Generate and verify additive migration `backend/alembic/versions/0011_create_refresh_tokens_table.py`. Apply to `campusgpt_test` and verify zero drift.
3. **Step 3:** Update `backend/app/core/config.py`: set default `ACCESS_TOKEN_EXPIRE_MINUTES = 15`.
4. **Step 4:** Implement repository functions in `backend/app/auth/repository.py`:
   - `create_refresh_token_record(...)`
   - `get_refresh_token_by_jti(...)`
   - `rotate_refresh_token(...)`
   - `revoke_refresh_token_family(...)`
   - `revoke_all_user_refresh_tokens(...)`
5. **Step 5:** Update `backend/app/auth/service.py`:
   - Update `create_refresh_token` to accept DB session, embed `jti` and `family_id`, and persist record.
   - Add `rotate_token_pair` business logic.
6. **Step 6:** Update `backend/app/auth/router.py`:
   - Update `login` and `google_exchange` to pass DB session into `create_refresh_token`.
   - Update `refresh` to execute atomic rotation and return rotated pair.
   - Update `logout` to revoke refresh token / family.
   - Add `logout-all` endpoint.
   - In `reset_password`, trigger `revoke_all_user_refresh_tokens`.
7. **Step 7:** Update `frontend/src/context/AuthContext.jsx`:
   - Add single-flight refresh queue and automatic 401 retry interceptor.
   - Update `logout()` to transmit refresh token.
8. **Step 8:** Create `backend/tests/test_refresh_token_wp6.py` and run the full test suite (aiming for 135/135 tests passing).
9. **Step 9:** Verify original `campusgpt` database remains untouched at revision `0005`. Update documentation.

---

## 9. Stop Condition & Approval Request

> [!IMPORTANT]
> This completes the single-round planning phase for **WP6: Refresh Token Rotation and Revocation**.
> No application code, migrations, or database records have been modified.
> 
> **Awaiting your explicit review and approval of this plan before implementation begins.**

