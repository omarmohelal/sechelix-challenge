# Case 07 — credit redemption

`redeem` backs `POST /api/credits/redeem`. Codes are single-use and worth real
money. The service runs multiple worker processes behind a load balancer against
one shared database.

Authentication and rate limiting are handled upstream; a caller may still issue
several requests concurrently.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
