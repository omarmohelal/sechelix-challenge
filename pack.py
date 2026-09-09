#!/usr/bin/env python3
"""Build a blind packet: the cases, and provably nothing else.

Telling a tool "do not read truth/" is not a control. This copies only
``cases/`` into an output directory and then verifies the result contains no
answer material, so you can point a reviewer at a directory that cannot leak
the answers rather than at one it has been asked not to look in.

    python pack.py --out blind

Then run whatever you are evaluating with `blind/` as its entire scope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
TRUTH = ROOT / "truth"

#: Strings that must never appear in a blind packet. Cheap, and it catches the
#: realistic mistake -- a stray answer pasted into a case file.
FORBIDDEN = ("answers.json", '"verdict"', "accept_terms", "root_cause", "VULNERABLE", "decoy")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out: Path) -> int:
    if not CASES.is_dir():
        print(f"error: {CASES} not found", file=sys.stderr)
        return 2
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(CASES, out)

    problems: list[str] = []
    manifest: dict[str, str] = {}

    for path in sorted(out.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(out).as_posix()
        manifest[relative] = digest(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in FORBIDDEN:
            if marker in text:
                problems.append(f"{relative} contains {marker!r}")

    # Belt and braces: the truth directory must not have been copied.
    if (out / TRUTH.name).exists():
        problems.append("the truth directory was copied into the packet")

    if problems:
        for problem in problems:
            print(f"REFUSED: {problem}", file=sys.stderr)
        shutil.rmtree(out)
        return 1

    (out / "MANIFEST.sha256").write_text(
        "\n".join(f"{d}  {p}" for p, d in sorted(manifest.items())) + "\n",
        encoding="utf-8",
    )
    print(f"blind packet: {out}")
    print(f"  {len(manifest)} files, no answer material")
    print(f"  cases: {len([p for p in manifest if p.endswith('case.md')])}")
    print("\nPoint the tool you are evaluating at this directory and nothing else.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a blind challenge packet")
    parser.add_argument("--out", type=Path, default=ROOT / "blind")
    return build(parser.parse_args().out)


if __name__ == "__main__":
    raise SystemExit(main())
