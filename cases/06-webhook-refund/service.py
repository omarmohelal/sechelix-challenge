"""Payment provider refund webhook."""

import hashlib
import hmac
import json

SIGNING_SECRET = None  # injected from the secret store at startup


def verify(body: bytes, signature_header: str) -> bool:
    expected = hmac.new(SIGNING_SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def handle_refund_webhook(db, body: bytes, signature_header: str) -> dict:
    if not verify(body, signature_header):
        raise PermissionError("bad signature")

    event = json.loads(body)
    if event["type"] != "refund.succeeded":
        return {"ignored": event["type"]}

    order_id = event["data"]["order_id"]
    amount = int(event["data"]["amount_cents"])

    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        raise KeyError(order_id)

    db.execute(
        "UPDATE customer_balance SET cents = cents + ? WHERE person_id = ?",
        (amount, order["person_id"]),
    )
    db.execute("UPDATE orders SET status = 'refunded' WHERE id = ?", (order_id,))
    db.commit()
    return {"credited": amount, "order": order_id}
