# Case 04 — document thumbnail

`make_thumbnail` runs when a user opens an uploaded PDF in the web viewer.
`document_id` and `page` both come from the request. Authorization for the
document is enforced by the caller and is not in scope.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
