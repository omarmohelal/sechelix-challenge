"""Restore a workspace from an uploaded backup archive."""

import pathlib
import zipfile

MAX_TOTAL_BYTES = 200 * 1024 * 1024


def restore(archive_path: pathlib.Path, workspace: pathlib.Path) -> list[str]:
    workspace.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    with zipfile.ZipFile(archive_path) as archive:
        total = sum(info.file_size for info in archive.infolist())
        if total > MAX_TOTAL_BYTES:
            raise ValueError("archive too large when expanded")

        for info in archive.infolist():
            if info.is_dir():
                continue
            if info.filename.startswith("/"):
                raise ValueError(f"absolute path in archive: {info.filename}")

            destination = workspace / info.filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, open(destination, "wb") as target:
                target.write(source.read())
            written.append(info.filename)

    return written
