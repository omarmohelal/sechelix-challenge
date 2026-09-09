"""Team invitations.

Changed in #4412 after a security report: accepting an invitation used to trust
the org_id in the request body. It now reads the org from the stored invitation.
"""


def accept_invite(db, actor, token: str) -> dict:
    invite = db.execute(
        "SELECT id, org_id, email, role, accepted FROM invite WHERE token = ?",
        (token,),
    ).fetchone()
    if invite is None or invite["accepted"]:
        raise PermissionError("invalid invitation")

    # #4412: org comes from the invitation, never from the caller.
    db.execute(
        "UPDATE person SET org_id = ?, role = ? WHERE id = ?",
        (invite["org_id"], invite["role"], actor["id"]),
    )
    db.execute("UPDATE invite SET accepted = 1 WHERE id = ?", (invite["id"],))
    db.commit()
    return {"org_id": invite["org_id"], "role": invite["role"]}


def preview_invite(db, token: str, org_id: int) -> dict:
    """Unauthenticated preview shown on the invitation landing page."""
    invite = db.execute(
        "SELECT email, role FROM invite WHERE token = ?", (token,)
    ).fetchone()
    if invite is None:
        raise KeyError("invalid invitation")
    org = db.execute(
        "SELECT name, plan, seat_count, billing_email FROM org WHERE id = ?",
        (org_id,),
    ).fetchone()
    return {
        "invited_email": invite["email"],
        "role": invite["role"],
        "organization": dict(org),
    }
