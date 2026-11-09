# Faculty Approval Workflow

**Status:** NOT IMPLEMENTED. PROPOSED in WP2. Interim approval path (Swagger + CLI vs temporary admin UI) is PENDING APPROVAL (PD-01). Staff/student email-domain assumption is PD-02.

## Actors
Applicant (a registered STUDENT who asked for FACULTY), Administrator, the system.

## Workflow
```mermaid
sequenceDiagram
    participant U as Applicant
    participant FE as Frontend (existing sign-up)
    participant API as FastAPI
    participant DB as PostgreSQL
    participant A as Admin (Swagger/CLI interim)
    U->>FE: Sign up, choose Faculty
    FE->>API: POST /api/v1/auth/register (role=FACULTY)
    API->>DB: create STUDENT user + role_requests(PENDING)
    API-->>FE: 201 (role STUDENT)
    Note over U: Signs in as a student - faculty features stay hidden
    A->>API: GET /api/v1/admin/role-requests?status=PENDING
    A->>API: POST /api/v1/admin/role-requests/{id}/approve
    API->>DB: user.role=FACULTY, request APPROVED (reviewer, time, note)
    API->>API: revoke refresh tokens (WP6), audit event (WP11)
    U->>API: next request: role read from DB
    API-->>U: faculty access granted
```

## States
`PENDING → APPROVED | REJECTED`. A user may have one open request at a time. A rejected user may re-apply after a configurable delay (PROPOSED default: 7 days).

## Endpoints (PROPOSED)
| Method | Path | Who | Purpose |
|---|---|---|---|
| GET | `/api/v1/admin/role-requests` | ADMIN | list, filter by status |
| POST | `/api/v1/admin/role-requests/{id}/approve` | ADMIN | approve with optional note |
| POST | `/api/v1/admin/role-requests/{id}/reject` | ADMIN | reject with reason |
| GET | `/api/v1/auth/me` | any | includes pending-request status (field name to be decided during implementation) |

## Rules
- The reviewer cannot be the applicant.
- Approval sets the role in one transaction with the status change.
- Both outcomes are recorded (reviewer, time, note) and, after WP11, audited.
- Notification to the applicant uses the notification module when it exists (P10); until then the status appears in `/auth/me`.
- Faculty privileges still require assignment to subjects/classes (P05+); approval alone does not grant access to any class data.

## Interim tooling
CLI: `python -m app.manage_role_requests list|approve|reject` (name illustrative; follows `create_admin.py`). A real admin screen arrives with the Admin Dashboard (P21).

## Verification requirements
Approval/rejection tests, self-approval block, concurrent double-approval safety (second call fails cleanly), and a check that pending users get 403 on faculty-only routes.
