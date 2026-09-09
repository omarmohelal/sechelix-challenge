# Case 05 — password reset token

`issue_reset_token` runs when someone submits the "forgot password" form. The
token is emailed as a link. `consume_reset_token` runs when that link is opened
and returns the account whose password may then be set.

`person.id` is a sequential integer. User enumeration through other endpoints is
out of scope; assume an attacker can learn a target's user id.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
