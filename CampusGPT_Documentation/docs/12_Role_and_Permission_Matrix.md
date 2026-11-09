# 12 — Role and Permission Matrix

**Status:** PROPOSED (only role enum + `require_role` exist today). Legend: **S** self/own, **A** assigned scope, **ALL** scoped by institution/department, **—** none, **R** read, **W** write.

| Resource / action | STUDENT | FACULTY (approved) | ADMIN | Notes |
|---|---|---|---|---|
| Own profile read/edit editable fields | S R/W | S R/W | S R/W | verified fields admin-only |
| Verified institutional fields | S R | S R | ALL W | |
| Student profiles of others | — | A R (limited) | ALL R/W | |
| Role requests | S create | S create (n/a) | ALL R/W | approval only by ADMIN, not own |
| Create/promote ADMIN | — | — | CLI only | never via public API |
| Attendance: own | S R | — | — | |
| Attendance: sessions and marking | — | A W | ALL R, correct with reason | |
| Attendance policy / geofence | — | — | ALL W | |
| Timetable: view | S R | S R | ALL R | |
| Timetable: edit master | — | request only | ALL W | |
| Assignments: create/evaluate | — | A W | ALL R | |
| Assignments: submit/view own | S W/R | — | — | |
| Notices: read | audience R | audience R | ALL R | |
| Notices: publish | — | A W | ALL W | designations widen scope |
| Documents: institutional read | audience R | audience R | ALL R | |
| Documents: upload | personal only | A W | ALL W | |
| Documents: personal | S R/W | S R/W | — | admin cannot read personal docs |
| AI chat: own conversations | S R/W | S R/W | S R/W | no cross-user access |
| AI retrieval | own + authorised | assigned + authorised | scoped | same ACL as download |
| Analytics | S R | A R | ALL R | small-group suppression |
| Placements: browse/apply | S W | — | — | |
| Placements: manage | — | coordinator designation | ALL W | |
| Opportunities: post | — | A W | ALL W | |
| Courses: recommendations | S R | — | — | |
| Courses: catalogue | — | — | ALL W | |
| Visual boards | S R/W (own) | S R/W (own) | — | sharing later |
| Biometrics: consent, enrol, delete own template | S W (own) | — | — | withdrawal deletes template |
| Biometric templates and raw images | — | — | — | nobody via the application; only the biometrics service |
| Face verification: verify own attendance | S W (own session) | — | — | consent required, manual fallback otherwise |
| Face verification: monitor results live | — | A R (outcomes/scores summary, own sessions) | ALL R | no images |
| Attendance manual mark / override | — | A W (reason required) | ALL R, W with reason | audited, previous value kept |
| Biometric policy, geofence, retention | — | — | ALL W | audited |
| Voice sessions (Vapi) | S W (own) | S W (own) | S W (own) | tool calls resolve the user from the voice session only |
| WebSocket chat | S (own conversations) | S (own) | S (own) | identity fixed at authentication |
| WebSocket live attendance | — | A (session owner) | — | ownership checked on connect |
| Audit logs | — | — | ALL R | append-only |
| System configuration, AI config | — | — | ALL W | |

## Designations (PD-14, PROPOSED)
HOD, Dean, Coordinator are stored as designation rows with a scope (department, institution, function). They add specific permissions to FACULTY users — for example HOD: department-level notices and analytics read; placement coordinator: manage placement opportunities. They never create a new role value.

## Enforcement requirements
1. Every route declares its allowed roles and calls the matching policy.
2. Tests cover every cell marked "—" with an expected 403/404.
3. AI tools use the same policy functions as HTTP routes.
