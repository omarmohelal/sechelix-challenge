"""Redeem a promotional credit code."""


def redeem(db, actor, code: str) -> dict:
    row = db.execute(
        "SELECT id, value_cents, redeemed_by FROM credit_code WHERE code = ?",
        (code,),
    ).fetchone()

    if row is None:
        raise KeyError("no such code")
    if row["redeemed_by"] is not None:
        raise ValueError("code already redeemed")

    db.execute(
        "UPDATE customer_balance SET cents = cents + ? WHERE person_id = ?",
        (row["value_cents"], actor["id"]),
    )
    db.execute(
        "UPDATE credit_code SET redeemed_by = ? WHERE id = ?",
        (actor["id"], row["id"]),
    )
    db.commit()
    return {"credited": row["value_cents"]}
