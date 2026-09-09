# Case 08 — team invitations

Both functions are reachable: `accept_invite` from `POST /api/invites/accept`
(authenticated) and `preview_invite` from `GET /invite/<token>?org=<id>`
(unauthenticated — the landing page a new user sees before signing up).

A previous security report about this file was fixed in #4412.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
