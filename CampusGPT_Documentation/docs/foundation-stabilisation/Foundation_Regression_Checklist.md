# Foundation Regression Checklist

Run after **every** work package and again at step 17. Record results honestly — never tick a box that was not executed.

## Automated (must be green)
- [ ] Backend suite on PostgreSQL `*_test` database
- [ ] Alembic: single head; upgrade from scratch; upgrade from a copy of real data; drift check clean
- [ ] `npm run lint`, `npm run build`
- [ ] Security-regression subset (C1, C2, C3, OAuth, rate limit, refresh)

## Behaviour that must remain unchanged (existing features)
- [ ] Email + password sign-up with OTP verification works from the unchanged UI
- [ ] Email + password sign-in works
- [ ] College selector and domain validation work
- [ ] Google sign-in and sign-up work for new and existing users
- [ ] Forgot-password and reset-password work
- [ ] `/me` returns the profile; `/health` responds
- [ ] Admin created by the CLI can sign in
- [ ] Existing user rows unchanged (compare counts and a checksum of ids)
- [ ] Landing, sign-in, sign-up pages render and look unchanged

## Security regressions that must stay fixed
- [ ] Passwordless Google account cannot log in with a password (C1)
- [ ] Five wrong OTP codes do not allow registration (C2)
- [ ] `role=ADMIN` is rejected; FACULTY needs approval (C3)
- [ ] No token in any URL
- [ ] Production config refuses default secrets
- [ ] Limits return 429 with `Retry-After`
- [ ] Reused refresh token revokes the family
- [ ] No sensitive value in logs
