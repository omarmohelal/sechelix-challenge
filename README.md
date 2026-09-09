# SecHelix Challenge

Ten small security cases. Seven have a real defect. Three do not, and all three
are written to look like the thing every pattern matcher is trained to flag.

You can score a tool — or yourself — on them in about ten minutes.

```bash
git clone https://github.com/omarmohelal/sechelix-challenge
cd sechelix-challenge
python pack.py --out blind          # cases only, provably no answers
# ... review blind/ and write your verdicts ...
python score.py my-answers.json
```

Python 3.10+. No dependencies.

## Why this exists

A corpus of vulnerable-only code measures whether a tool can *find* things. It
cannot measure whether a tool can *stop*. On such a corpus, a reviewer that
flags every file scores perfectly and is useless in a real repository, where the
cost of a wrong finding is an engineer's afternoon and the cost of several is
that nobody reads the next one.

So the decoys here are not filler. They are three of the ten, they are the
cases most likely to trip a keyword rule, and getting them wrong costs exactly
what missing a real bug costs.

The cases are also written so that the surface signal points the wrong way:

- the case with a real SQL-shaped f-string is **safe**, and the case where the
  f-string is genuinely harmless is the one with a **real authorization bug**
  three lines below it;
- one case has a correct HMAC signature check and a real defect that has nothing
  to do with the HMAC;
- one case is a **remediation regression** — a previous fix, correctly applied
  at one call site, and a sibling route that kept the original pattern.

## Rules

**Scope the tool to `blind/`.** `python pack.py` copies only `cases/` and then
verifies the result contains no answer material, refusing and deleting the
packet if it finds any. Telling a reviewer "do not read `truth/`" is not a
control; handing it a directory that cannot contain the answers is.

**`UNKNOWN` is a legitimate answer.** It scores zero rather than counting as an
error. A reviewer that says "I could not determine this" has behaved correctly.
One that guesses has not, and a score that cannot tell the two apart is
measuring the wrong quantity.

**Name the class on a vulnerable case.** "Something is wrong here" is not a
finding. Matching is generous — any accepted synonym, substring,
case-insensitive — because the question is whether you identified the defect,
not whether you used our spelling of it.

## Submission format

```json
{
  "01-receipt-export": {"verdict": "VULNERABLE", "class": "IDOR"},
  "02-report-sort":    {"verdict": "SAFE"},
  "08-invite-accept":  {"verdict": "UNKNOWN"}
}
```

`verdict` is `VULNERABLE`, `SAFE` or `UNKNOWN`. `class` is free text, required
only to score a `VULNERABLE` verdict as fully correct. An omitted case counts as
`UNKNOWN`. See `answers.example.json`.

## Scoring

```text
correct                     6/10
right verdict, wrong class  0
missed                      1
false positives             2
abstained                   1
```

Five columns, no single headline number. Precision and recall are different
failures with different costs, and an aggregate that averages them hides the
thing you needed to know. "Right verdict, wrong class" is separated out because
spotting that a file is wrong without identifying why is real but partial.

## Coverage

| Case | Surface |
|---|---|
| 01 | data export, object authorization |
| 02 | dynamic SQL construction |
| 03 | outbound fetch from a user-supplied URL |
| 04 | subprocess invocation on request-derived arguments |
| 05 | account recovery token generation |
| 06 | signed payment webhook |
| 07 | single-use credit redemption under concurrency |
| 08 | invitation flow, after a previous security fix |
| 09 | archive extraction |
| 10 | cache key derivation |

Which are real and which are decoys is in `truth/answers.json`. Read it after
you have answered, not before — each entry carries the class, CWE, root cause,
smallest fix, and for the safe cases, why it looks dangerous.

## Limitations, stated plainly

**Ten hand-written cases are not a benchmark.** They measure a submission on
these ten cases and support no general accuracy claim about any tool. Anyone
quoting a number from here as a capability claim is overreading it, including us.

**They are single files.** Real defects hide in the interaction between files,
services and deploys. Every case here is deliberately small enough to hold in
your head, which makes them easier than the real thing.

**They are answerable from source alone.** No case needs a running system, which
excludes an entire category of real vulnerability.

**The ground truth is our judgement.** It is public and arguable. If you think a
verdict is wrong, open an issue — a case that turns out to be ambiguous is a bug
in the case, and we would rather fix it than defend it.

**Cases can leak into training data** once they are public. That is unavoidable
for an open challenge and is a reason to treat old scores with suspicion.

## Contributing a case

Good cases are small, realistic, and wrong in one specific way — or right in a
way that looks wrong. A case is more valuable when its surface signal points
away from the truth.

Open a PR adding `cases/<nn>-<slug>/{case.md,service.py}` and the matching
`truth/answers.json` entry. `python -m unittest test_challenge` must pass; it
checks, among other things, that the prompt does not give the answer away, that
guessing `VULNERABLE` everywhere fails, and that guessing `SAFE` everywhere
fails too.

## About

Built alongside [SecHelix](https://github.com/omarmohelal/SecHelix), an
evidence-first AppSec Agent Skill that sends every candidate finding to an
independent verifier whose job is to disprove it before it is reported.

The challenge is deliberately tool-neutral: nothing here is SecHelix-specific,
and it is as fair to a scanner, another agent, or a human reviewer as it is to
us. If it is useful, a star on either repository helps other people find it.

Apache-2.0.
