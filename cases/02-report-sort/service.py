"""Report ordering for the spend dashboard."""

COLUMNS = {
    "date": "created_at",
    "amount": "amount_cents",
    "merchant": "merchant",
    "status": "status",
}
DIRECTIONS = {"asc": "ASC", "desc": "DESC"}


def spend_report(db, org_id: int, sort: str = "date", direction: str = "desc"):
    column = COLUMNS.get(sort)
    if column is None:
        raise ValueError(f"unsupported sort field: {sort}")
    order = DIRECTIONS.get(direction.lower())
    if order is None:
        raise ValueError(f"unsupported direction: {direction}")

    return db.execute(
        f"SELECT merchant, amount_cents, status, created_at FROM receipt "
        f"WHERE org_id = ? ORDER BY {column} {order} LIMIT 200",
        (org_id,),
    ).fetchall()
