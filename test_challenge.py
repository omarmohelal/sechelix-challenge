"""The challenge holds itself to the standard it asks of a submission.

    python -m unittest test_challenge -v
"""

import ast
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
TRUTH = json.loads((ROOT / "truth/answers.json").read_text(encoding="utf-8"))["cases"]

sys.path.insert(0, str(ROOT))
import score as scorer  # noqa: E402


def case_ids():
    return sorted(p.name for p in CASES.iterdir() if p.is_dir())


class CasesAreWellFormed(unittest.TestCase):
    def test_every_case_has_both_files(self):
        for case in case_ids():
            with self.subTest(case=case):
                self.assertTrue((CASES / case / "case.md").is_file())
                self.assertTrue((CASES / case / "service.py").is_file())

    def test_every_case_is_valid_python(self):
        """A case that does not parse is a puzzle about syntax, not security."""
        for case in case_ids():
            with self.subTest(case=case):
                source = (CASES / case / "service.py").read_text(encoding="utf-8")
                ast.parse(source)

    def test_cases_and_truth_agree_exactly(self):
        self.assertEqual(case_ids(), sorted(TRUTH))

    def test_case_files_never_state_the_answer(self):
        """The prompt must not tell you which way it goes."""
        giveaways = ("vulnerable", "safe implementation", "this is a decoy",
                     "false positive", "no defect", "the bug is")
        for case in case_ids():
            text = (CASES / case / "case.md").read_text(encoding="utf-8").lower()
            for word in giveaways:
                with self.subTest(case=case, word=word):
                    self.assertNotIn(word, text)

    def test_every_case_asks_the_same_question(self):
        """Varying the prompt varies the difficulty for reasons unrelated to the code."""
        for case in case_ids():
            text = (CASES / case / "case.md").read_text(encoding="utf-8")
            self.assertIn("Is there a security defect in this file?", text)


class TruthIsHonest(unittest.TestCase):
    def test_the_set_is_not_all_one_answer(self):
        verdicts = [v["verdict"] for v in TRUTH.values()]
        self.assertGreaterEqual(verdicts.count("SAFE"), 3, "too few decoys to punish guessing")
        self.assertGreaterEqual(verdicts.count("VULNERABLE"), 5)

    def test_guessing_vulnerable_everywhere_does_not_pass(self):
        """The point of the decoys, stated as a test."""
        always = {case: {"verdict": "VULNERABLE", "class": "something"} for case in TRUTH}
        result = scorer.score(always, TRUTH)
        self.assertGreaterEqual(result["totals"]["FALSE_POSITIVE"], 3)
        self.assertLess(result["totals"]["CORRECT"], len(TRUTH) // 2)

    def test_guessing_safe_everywhere_does_not_pass(self):
        always = {case: {"verdict": "SAFE"} for case in TRUTH}
        result = scorer.score(always, TRUTH)
        self.assertGreaterEqual(result["totals"]["MISSED"], 5)

    def test_vulnerable_cases_carry_a_class_and_a_fix(self):
        for case, entry in TRUTH.items():
            if entry["verdict"] != "VULNERABLE":
                continue
            with self.subTest(case=case):
                self.assertTrue(entry["class"])
                self.assertTrue(entry["cwe"])
                self.assertTrue(entry["fix"])
                self.assertTrue(entry["root_cause"])
                self.assertTrue(entry["accept_terms"])

    def test_safe_cases_say_why_they_look_bad(self):
        """A decoy that does not look dangerous is not testing anything."""
        for case, entry in TRUTH.items():
            if entry["verdict"] != "SAFE":
                continue
            with self.subTest(case=case):
                self.assertIsNone(entry["class"])
                self.assertTrue(entry["why_it_looks_bad"])

    def test_no_accuracy_claim_anywhere(self):
        banned = ("industry-leading", "state of the art", "best in class",
                  "outperforms", "% accuracy", "sota")
        for path in list(ROOT.rglob("*.md")) + [ROOT / "truth/answers.json"]:
            if "blind" in path.parts or ".git" in path.parts:
                continue
            text = path.read_text(encoding="utf-8").lower()
            for phrase in banned:
                with self.subTest(path=path.name, phrase=phrase):
                    self.assertNotIn(phrase, text)


class Scoring(unittest.TestCase):
    def test_a_perfect_submission_scores_perfectly(self):
        perfect = {
            case: (
                {"verdict": "SAFE"} if entry["verdict"] == "SAFE"
                else {"verdict": "VULNERABLE", "class": entry["class"]}
            )
            for case, entry in TRUTH.items()
        }
        result = scorer.score(perfect, TRUTH)
        self.assertEqual(result["totals"]["CORRECT"], len(TRUTH))

    def test_accept_terms_are_honoured(self):
        submission = {
            case: (
                {"verdict": "SAFE"} if entry["verdict"] == "SAFE"
                else {"verdict": "VULNERABLE", "class": entry["accept_terms"][0]}
            )
            for case, entry in TRUTH.items()
        }
        self.assertEqual(scorer.score(submission, TRUTH)["totals"]["CORRECT"], len(TRUTH))

    def test_right_verdict_wrong_class_is_its_own_column(self):
        submission = {"01-receipt-export": {"verdict": "VULNERABLE", "class": "xss"}}
        rows = {r["case"]: r for r in scorer.score(submission, TRUTH)["rows"]}
        self.assertEqual(rows["01-receipt-export"]["outcome"], "RIGHT_VERDICT_WRONG_CLASS")

    def test_unknown_is_abstention_not_an_error(self):
        submission = {case: {"verdict": "UNKNOWN"} for case in TRUTH}
        totals = scorer.score(submission, TRUTH)["totals"]
        self.assertEqual(totals["ABSTAINED"], len(TRUTH))
        self.assertEqual(totals["MISSED"], 0)
        self.assertEqual(totals["FALSE_POSITIVE"], 0)

    def test_an_omitted_case_defaults_to_abstention(self):
        totals = scorer.score({}, TRUTH)["totals"]
        self.assertEqual(totals["ABSTAINED"], len(TRUTH))

    def test_a_bad_verdict_word_is_refused(self):
        with self.assertRaises(scorer.SubmissionError):
            scorer.score({"01-receipt-export": {"verdict": "PROBABLY"}}, TRUTH)

    def test_an_unknown_case_id_is_refused(self):
        with self.assertRaises(scorer.SubmissionError):
            scorer.score({"99-not-a-case": {"verdict": "SAFE"}}, TRUTH)

    def test_the_example_submission_scores(self):
        result = subprocess.run(
            [sys.executable, "score.py", "answers.example.json"],
            cwd=str(ROOT), capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("false positives             2", result.stdout)


class BlindPacket(unittest.TestCase):
    def test_the_packet_contains_no_answer_material(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "blind"
            result = subprocess.run(
                [sys.executable, "pack.py", "--out", str(out)],
                cwd=str(ROOT), capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((out / "truth").exists())
            self.assertFalse(list(out.rglob("answers.json")))

            for path in out.rglob("*"):
                if not path.is_file() or path.name == "MANIFEST.sha256":
                    continue
                text = path.read_text(encoding="utf-8")
                for marker in ("accept_terms", "root_cause", '"verdict"'):
                    self.assertNotIn(marker, text, f"{path.name} leaks {marker}")

    def test_the_packet_has_every_case(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "blind"
            subprocess.run(
                [sys.executable, "pack.py", "--out", str(out)],
                cwd=str(ROOT), capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(
                sorted(p.name for p in out.iterdir() if p.is_dir()), case_ids()
            )

    def test_pack_refuses_and_cleans_up_when_a_case_leaks(self):
        """The check is only worth having if it actually refuses."""
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "challenge"
            shutil.copytree(ROOT, staging, ignore=shutil.ignore_patterns(
                ".git", "blind", "__pycache__"))
            leak = staging / "cases" / case_ids()[0] / "case.md"
            leak.write_text(leak.read_text(encoding="utf-8") + '\n"verdict": "VULNERABLE"\n',
                            encoding="utf-8")
            out = Path(directory) / "blind"
            result = subprocess.run(
                [sys.executable, "pack.py", "--out", str(out)],
                cwd=str(staging), capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("REFUSED", result.stderr)
            self.assertFalse(out.exists(), "a refused packet must not be left on disk")


class QuizPage(unittest.TestCase):
    """The shareable page is generated. A stale one is worse than none."""

    def test_the_committed_page_matches_the_current_cases(self):
        import build_quiz

        committed = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertEqual(
            committed, build_quiz.build(),
            "docs/index.html is stale -- run `python build_quiz.py` and commit the result",
        )

    def test_every_case_reaches_the_page(self):
        page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        for case in case_ids():
            with self.subTest(case=case):
                self.assertIn(case, page)

    def test_the_page_states_the_limitation(self):
        """The honesty line is load-bearing; it must not get edited out."""
        # Whitespace-normalised: the template hard-wraps, so a literal match
        # would fail on a reflow rather than on the sentence going missing.
        page = " ".join((ROOT / "docs/index.html").read_text(encoding="utf-8").split())
        self.assertIn("not a benchmark and support no general claim", page)
        self.assertIn("Abstaining scores zero rather than counting as an error", page)
        self.assertIn("No signup, nothing stored, nothing sent anywhere", page)

    def test_the_page_makes_no_accuracy_claim(self):
        page = (ROOT / "docs/index.html").read_text(encoding="utf-8").lower()
        for phrase in ("industry-leading", "% accuracy", "outperforms", "best in class"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
