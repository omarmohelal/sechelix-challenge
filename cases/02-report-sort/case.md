# Case 02 — report sort

`spend_report` backs the spend dashboard. `sort` and `direction` come straight
from the query string. `org_id` is the authenticated caller's organization and
is not attacker-controlled.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
