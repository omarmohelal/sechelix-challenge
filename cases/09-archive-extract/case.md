# Case 09 — workspace restore

`restore` runs when a user uploads a `.zip` backup to restore their workspace.
`archive_path` is the uploaded file. `workspace` is a per-user directory the
service owns. The process runs as a service account with write access to the
application's own installation directory.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
