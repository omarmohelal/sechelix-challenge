"""Password reset tokens."""

import hashlib
import time


def issue_reset_token(db, email: str) -> str | None:
    person = db.execute("SELECT id FROM person WHERE email = ?", (email,)).fetchone()
    if person is None:
        return None

    # Unique per user per second, and unguessable without knowing the user id.
    seed = f"{person['id']}:{int(time.time())}"
    token = hashlib.sha256(seed.encode()).hexdigest()

    db.execute(
        "INSERT INTO reset_token (person_id, token, created_at) VALUES (?, ?, ?)",
        (person["id"], token, int(time.time())),
    )
    db.commit()
    return token


def consume_reset_token(db, token: str):
    row = db.execute(
        "SELECT person_id FROM reset_token WHERE token = ?", (token,)
    ).fetchone()
    if row is None:
        raise PermissionError("invalid reset token")
    db.execute("DELETE FROM reset_token WHERE token = ?", (token,))
    db.commit()
    return row["person_id"]
