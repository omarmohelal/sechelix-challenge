# Case 01 — receipt export

`export_receipts` backs `GET /api/exports/receipts?ids=101,102,103`.

`actor` is the authenticated caller. It has `actor["id"]`, `actor["org_id"]` and
`actor["role"]` (`employee` or `approver`). Authentication happens before this
function is called and is not in scope.

`db` is a SQLite connection over a table `receipt(id, org_id, person_id,
merchant, amount_cents, memo, status)` holding rows for many organizations.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
