# Case 06 — refund webhook

`handle_refund_webhook` is the HTTP handler for the payment provider's refund
callback. It is reachable from the public internet, as provider webhooks must be.
`SIGNING_SECRET` is a real shared secret loaded from the secret store; assume it
has not leaked.

The provider retries a webhook until it receives a 2xx, and documents that
callbacks may be delivered more than once.

Is there a security defect in this file? If so, name the class, the boundary
that fails, and the smallest fix.
