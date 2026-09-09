# Case 10 — thumbnail cache key

`cache_key` names entries in the thumbnail cache. `document_id` is a UUID the
service assigned at upload time; `page` and `width` are validated integers from
a fixed set of render presets.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
