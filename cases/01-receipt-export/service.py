"""Receipt export. Called by GET /api/exports/receipts?ids=101,102,103"""

from typing import Iterable


def parse_ids(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part.strip()]


def export_receipts(db, actor, raw_ids: str) -> list[dict]:
    """Return the requested receipts as export rows."""
    ids = parse_ids(raw_ids)
    if len(ids) > 500:
        raise ValueError("too many ids in one export")

    placeholders = ",".join("?" for _ in ids)
    rows = db.execute(
        f"SELECT id, org_id, merchant, amount_cents, memo FROM receipt "
        f"WHERE id IN ({placeholders})",
        ids,
    ).fetchall()

    # The UI only ever shows the caller their own organization's receipts.
    return [
        {
            "id": row["id"],
            "merchant": row["merchant"],
            "amount_cents": row["amount_cents"],
            "memo": row["memo"],
        }
        for row in rows
    ]


def render_csv(rows: Iterable[dict]) -> str:
    header = "id,merchant,amount_cents,memo"
    body = "\n".join(
        f"{r['id']},{r['merchant']},{r['amount_cents']},{r['memo']}" for r in rows
    )
    return f"{header}\n{body}\n"
