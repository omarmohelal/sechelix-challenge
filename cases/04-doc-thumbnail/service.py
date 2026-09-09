"""Render a thumbnail for an uploaded document."""

import pathlib
import subprocess
import uuid

RENDERER = "/usr/bin/pdftoppm"
STORAGE = pathlib.Path("/var/lib/app/documents")
THUMBS = pathlib.Path("/var/lib/app/thumbnails")


def _stored_path(document_id: str) -> pathlib.Path:
    """Documents are addressed by the UUID we assigned at upload time."""
    identifier = uuid.UUID(document_id)          # raises ValueError if not a UUID
    path = STORAGE / f"{identifier}.pdf"
    if not path.is_file():
        raise FileNotFoundError(document_id)
    return path


def make_thumbnail(document_id: str, page: int = 1) -> pathlib.Path:
    source = _stored_path(document_id)
    if not 1 <= page <= 500:
        raise ValueError("page out of range")

    destination = THUMBS / str(uuid.UUID(document_id))
    subprocess.run(
        [RENDERER, "-png", "-f", str(page), "-l", str(page),
         "-scale-to", "320", str(source), str(destination)],
        check=True,
        timeout=30,
    )
    return destination.with_suffix(".png")
