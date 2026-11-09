# Role Escalation Prevention (defect C3)

**Status:** IMPLEMENTED BUT DEFECTIVE (PO-RV). Fix PROPOSED in WP2 (user decision D-06).

## Current behaviour (audit-reported)
`RegisterRequest.role` (default STUDENT) accepts ADMIN, FACULTY or STUDENT, and `service.register_user` passes it to `repository.create_user`. The UI offers Student and Faculty only, but the API accepts ADMIN from any caller. Authorisation reads the role from the database (`get_current_user` → `require_role`), so promotion by a caller is immediately effective.

## Rules (PROPOSED)
1. Public registration creates STUDENT accounts only.
2. A requested FACULTY role is recorded as a PENDING request; it grants nothing.
3. ADMIN can never be requested publicly (422).
4. ADMIN accounts are created only through the CLI (`create_admin`) or another explicitly authorised administrative process.
5. Only an authenticated ADMIN can approve or reject faculty requests.
6. An admin cannot change their own role or approve their own request.
7. Existing elevated accounts are **never auto-downgraded**; they are listed in WP0 and reviewed by the owner.
8. Google-created accounts are always STUDENT.
9. Roles are read from the database on every request; the JWT `role` claim is informational only. Approval and demotion therefore take effect immediately.
10. Designations (HOD/Dean/Coordinator) are permissions layered on roles (PD-14), not roles.

## Attack paths closed
| Path | Closed by |
|---|---|
| `POST /register` with `role=ADMIN` | Rule 3 |
| Student picks Faculty in the UI | Rules 1–2 |
| Google sign-up as faculty | Rule 8 |
| Promotion via profile update (future) | Rule 4–6 plus module-level checks in P05/P21 |

## Tests
See `WP2_Authentication_Security.md`. Required: ADMIN → 422; FACULTY → STUDENT + PENDING; pending user → 403 on faculty endpoints; student → 403 on admin endpoints; approval → immediate access; self-approval blocked.
