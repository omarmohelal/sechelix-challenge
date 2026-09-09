#!/usr/bin/env python3
"""Score a submission against the ground truth.

    python score.py answers.example.json

The submission is a JSON object mapping case id to a verdict:

    {
      "01-receipt-export": {"verdict": "VULNERABLE", "class": "BOLA"},
      "02-report-sort":    {"verdict": "SAFE"},
      "03-avatar-import":  {"verdict": "UNKNOWN"}
    }

Three deliberate choices, because a scorer's defaults are an argument about what
matters:

**A false positive costs the same as a miss.** Most published comparisons count
only what a tool found. A tool that flags all ten cases scores 7/10 on recall
and is useless. Both error columns are reported and neither is hidden in an
aggregate.

**UNKNOWN is not wrong.** It scores zero rather than counting as an error. A
reviewer who says "I could not determine this" has behaved correctly; one who
guesses has not. A tool that answers three cases confidently and abstains on
seven is a different thing from one that gets three right and seven wrong, and a
score that cannot tell them apart is measuring the wrong quantity.

**The class must match, on a vulnerable case.** "Something is wrong here" is not
a finding. Matching is generous — any accepted term for the case, substring,
case-insensitive — because the point is whether the reviewer identified the
defect, not whether they used the repository's spelling of it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRUTH = ROOT / "truth/answers.json"

VERDICTS = {"VULNERABLE", "SAFE", "UNKNOWN"}


class SubmissionError(ValueError):
    """The submission cannot be scored."""


def load_truth() -> dict:
    return json.loads(TRUTH.read_text(encoding="utf-8"))["cases"]


def normalise(value: str) -> str:
    return " ".join(str(value).lower().replace("_", " ").replace("-", " ").split())


def class_matches(claimed: str | None, expected: dict) -> bool:
    if not claimed:
        return False
    text = normalise(claimed)
    terms = [normalise(t) for t in expected.get("accept_terms", [])]
    terms.append(normalise(expected["class"] or ""))
    return any(term and term in text for term in terms if term)


def score(submission: dict, truth: dict) -> dict:
    if not isinstance(submission, dict):
        raise SubmissionError("submission must be a JSON object keyed by case id")

    unknown_keys = sorted(set(submission) - set(truth))
    if unknown_keys:
        raise SubmissionError(f"unknown case id(s): {', '.join(unknown_keys)}")

    rows = []
    for case_id in sorted(truth):
        expected = truth[case_id]
        answer = submission.get(case_id) or {}
        if not isinstance(answer, dict):
            raise SubmissionError(f"{case_id}: answer must be an object")

        verdict = str(answer.get("verdict", "UNKNOWN")).upper()
        if verdict not in VERDICTS:
            raise SubmissionError(
                f"{case_id}: verdict must be one of {sorted(VERDICTS)}, got {verdict!r}"
            )

        truth_verdict = expected["verdict"]
        if verdict == "UNKNOWN":
            outcome = "ABSTAINED"
        elif truth_verdict == "VULNERABLE" and verdict == "VULNERABLE":
            outcome = (
                "CORRECT" if class_matches(answer.get("class"), expected)
                else "RIGHT_VERDICT_WRONG_CLASS"
            )
        elif truth_verdict == "SAFE" and verdict == "SAFE":
            outcome = "CORRECT"
        elif truth_verdict == "SAFE" and verdict == "VULNERABLE":
            outcome = "FALSE_POSITIVE"
        else:
            outcome = "MISSED"

        rows.append(
            {
                "case": case_id,
                "truth": truth_verdict,
                "answered": verdict,
                "claimed_class": answer.get("class"),
                "expected_class": expected["class"],
                "outcome": outcome,
            }
        )

    tally = {
        key: sum(1 for r in rows if r["outcome"] == key)
        for key in (
            "CORRECT", "RIGHT_VERDICT_WRONG_CLASS", "MISSED",
            "FALSE_POSITIVE", "ABSTAINED",
        )
    }
    return {"rows": rows, "totals": tally, "case_count": len(rows)}


def render(result: dict) -> str:
    width = max(len(r["case"]) for r in result["rows"])
    lines = [
        f"{'case'.ljust(width)}  {'truth':<10} {'answered':<10} outcome",
        f"{'-' * width}  {'-' * 10} {'-' * 10} {'-' * 26}",
    ]
    for row in result["rows"]:
        lines.append(
            f"{row['case'].ljust(width)}  {row['truth']:<10} "
            f"{row['answered']:<10} {row['outcome']}"
        )

    totals = result["totals"]
    total = result["case_count"]
    lines += [
        "",
        f"correct                     {totals['CORRECT']}/{total}",
        f"right verdict, wrong class  {totals['RIGHT_VERDICT_WRONG_CLASS']}",
        f"missed                      {totals['MISSED']}",
        f"false positives             {totals['FALSE_POSITIVE']}",
        f"abstained                   {totals['ABSTAINED']}",
        "",
        "Ten hand-written cases measure this submission on these ten cases.",
        "They are not a benchmark and support no general accuracy claim.",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Score a challenge submission")
    parser.add_argument("submission", type=Path)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    try:
        submission = json.loads(args.submission.read_text(encoding="utf-8"))
        submission.pop("$comment", None)
        result = score(submission, load_truth())
    except (OSError, json.JSONDecodeError, SubmissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
