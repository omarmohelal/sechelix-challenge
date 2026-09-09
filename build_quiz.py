#!/usr/bin/env python3
"""Generate the shareable quiz page from the cases and the ground truth.

The page is generated rather than hand-written for the same reason everything
else here is checked: a quiz whose answers have drifted from `truth/answers.json`
is worse than no quiz. `test_challenge.py` fails if `docs/index.html` is stale.

    python build_quiz.py

The answers are embedded in the page, which is fine — `truth/answers.json` is
public and always has been. The blind packet from `pack.py` is the artifact that
must stay answer-free, and it is built separately.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "cases"
TRUTH = json.loads((ROOT / "truth/answers.json").read_text(encoding="utf-8"))["cases"]
OUT = ROOT / "docs" / "index.html"

REPO = "https://github.com/omarmohelal/sechelix-challenge"
SECHELIX = "https://github.com/omarmohelal/SecHelix"


def prompt_of(case: str) -> str:
    """The case brief, minus the heading and the question every case shares."""
    text = (CASES / case / "case.md").read_text(encoding="utf-8")
    body = text.split("\n", 1)[1]
    body = body.replace(
        "Is there a security defect in this file? If so, name the class, the boundary\nthat fails, and the smallest fix.",
        "",
    )
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def md_inline(text: str) -> str:
    """Backticks and bold only. No Markdown library for one page."""
    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out.replace("\n\n", "</p><p>").replace("\n", " ")


def build_cases() -> list[dict]:
    payload = []
    for case in sorted(TRUTH):
        entry = TRUTH[case]
        payload.append(
            {
                "id": case,
                "title": case.split("-", 1)[1].replace("-", " "),
                "prompt": md_inline(prompt_of(case)),
                "code": (CASES / case / "service.py").read_text(encoding="utf-8"),
                "verdict": entry["verdict"],
                "cls": entry["class"] or "",
                "cwe": entry.get("cwe") or "",
                "summary": md_inline(entry["summary"]),
                "why": md_inline(entry.get("why_it_looks_bad", "")),
                "fix": md_inline(entry.get("fix", "")),
            }
        )
    return payload


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Can you tell the real bug from the decoy? &middot; SecHelix Challenge</title>
<meta name="description" content="Ten small AppSec cases. Seven have a real defect, three are decoys written to look like what scanners flag. A false positive costs exactly what a miss costs.">
<meta property="og:title" content="Can you tell the real bug from the decoy?">
<meta property="og:description" content="Ten AppSec cases. Three are decoys. A false positive costs exactly what a miss costs.">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{--bg:#fbfbfa;--fg:#1a1a19;--mut:#6b6b68;--line:#e3e3e0;--card:#fff;--code:#f6f6f4;--ok:#0d7a4a;--no:#b4341f;--accent:#5b3fa8}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececea;--mut:#9a9a96;--line:#2c2c30;--card:#1c1c1f;--code:#0f0f11;--ok:#4ade80;--no:#f87171;--accent:#a78bfa}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:2.5rem 1.25rem 5rem}
h1{font-size:1.9rem;line-height:1.25;margin:0 0 .6rem;letter-spacing:-.02em}
.sub{color:var(--mut);margin:0 0 1.6rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1.25rem;margin:0 0 1.25rem}
.meta{display:flex;justify-content:space-between;align-items:center;gap:1rem;color:var(--mut);font-size:.85rem;margin-bottom:.5rem}
.case-title{font-weight:600;color:var(--fg);text-transform:capitalize}
pre{background:var(--code);border:1px solid var(--line);border-radius:8px;padding:1rem;overflow-x:auto;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:1rem 0}
code{background:var(--code);padding:.12em .35em;border-radius:4px;font:.9em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre code{background:none;padding:0}
.btns{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1rem}
button{font:inherit;font-weight:600;padding:.6rem 1.1rem;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
button:hover{border-color:var(--accent)}
button:disabled{opacity:.45;cursor:default}
.reveal{margin-top:1rem;padding:1rem;border-radius:8px;border:1px solid var(--line);background:var(--code)}
.reveal p{margin:.5rem 0}
.tag{font-weight:700;letter-spacing:.04em;font-size:.8rem}
.right{color:var(--ok)} .wrong{color:var(--no)}
.prog{color:var(--mut);font-size:.85rem;margin-bottom:1rem}
table{width:100%;border-collapse:collapse;margin:1rem 0}
td{padding:.4rem 0;border-bottom:1px solid var(--line)}
td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
a{color:var(--accent)}
.small{font-size:.85rem;color:var(--mut)}
.hidden{display:none}
</style>
</head>
<body>
<div class="wrap">
<h1>One real vulnerability. One scary-looking false positive.<br>Can you tell which is which?</h1>
<p class="sub">Ten small AppSec cases. Seven have a real defect. Three do not &mdash; and all three are
written to look like exactly what a scanner flags. Getting a decoy wrong costs the same as missing a
real bug, because in a real queue it does.</p>
<p class="sub small">No signup, nothing stored, nothing sent anywhere. About five minutes.</p>

<div id="quiz"></div>
<div id="result" class="hidden"></div>
</div>

<script>
const CASES = __CASES__;
let i = 0, answers = [];

const el = (h) => { const d = document.createElement('div'); d.innerHTML = h; return d.firstElementChild; };

function render() {
  const q = document.getElementById('quiz');
  q.innerHTML = '';
  if (i >= CASES.length) return finish();
  const c = CASES[i];
  q.appendChild(el(`
    <div class="card">
      <div class="prog">Case ${i + 1} of ${CASES.length}</div>
      <div class="meta"><span class="case-title">${c.title}</span></div>
      <p>${c.prompt}</p>
      <pre><code>${c.code.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</code></pre>
      <div class="btns">
        <button data-a="VULNERABLE">Has a defect</button>
        <button data-a="SAFE">Safe as written</button>
        <button data-a="UNKNOWN">Can't tell</button>
      </div>
      <div id="rev"></div>
    </div>`));
  q.querySelectorAll('button').forEach(b => b.onclick = () => answer(b.dataset.a));
}

function answer(a) {
  const c = CASES[i];
  const correct = a === c.verdict;
  answers.push({id: c.id, answered: a, truth: c.verdict, correct, abstained: a === 'UNKNOWN'});
  document.querySelectorAll('#quiz button').forEach(b => b.disabled = true);
  const verdictLine = a === 'UNKNOWN'
    ? `<span class="tag">ABSTAINED</span> &mdash; that scores zero, not a penalty. Truth: <strong>${c.verdict}</strong>.`
    : (correct ? `<span class="tag right">CORRECT</span>` : `<span class="tag wrong">WRONG</span>`)
      + ` &mdash; this one is <strong>${c.verdict}</strong>${c.cls ? ' (' + c.cls + (c.cwe ? ', ' + c.cwe : '') + ')' : ''}.`;
  document.getElementById('rev').appendChild(el(`
    <div class="reveal">
      <p>${verdictLine}</p>
      <p>${c.summary}</p>
      ${c.why ? `<p class="small"><strong>Why it looks dangerous:</strong> ${c.why}</p>` : ''}
      ${c.fix ? `<p class="small"><strong>Smallest fix:</strong> ${c.fix}</p>` : ''}
      <div class="btns"><button id="next">${i + 1 < CASES.length ? 'Next case' : 'See your score'}</button></div>
    </div>`));
  document.getElementById('next').onclick = () => { i++; render(); };
  document.getElementById('next').scrollIntoView({behavior: 'smooth', block: 'center'});
}

function finish() {
  const t = {
    correct: answers.filter(a => a.correct).length,
    missed: answers.filter(a => !a.correct && !a.abstained && a.truth === 'VULNERABLE').length,
    fp: answers.filter(a => !a.correct && !a.abstained && a.truth === 'SAFE').length,
    abstained: answers.filter(a => a.abstained).length,
  };
  const r = document.getElementById('result');
  r.className = '';
  r.appendChild(el(`
    <div class="card">
      <h2 style="margin-top:0">Your score</h2>
      <table>
        <tr><td>Correct</td><td>${t.correct}/${CASES.length}</td></tr>
        <tr><td>Missed a real defect</td><td>${t.missed}</td></tr>
        <tr><td>Flagged something safe</td><td>${t.fp}</td></tr>
        <tr><td>Abstained</td><td>${t.abstained}</td></tr>
      </table>
      <p class="small">Two error columns, no single number. Precision and recall are different
      failures with different costs, and an average hides the one you needed to know.
      <strong>Abstaining scores zero rather than counting as an error</strong> &mdash; "I could not
      determine this" is a different behaviour from guessing.</p>
      <p class="small">Ten hand-written cases measure you on these ten cases. They are not a
      benchmark and support no general claim about anyone, including us.</p>
      <p><strong>Now run your scanner on it.</strong> The same ten cases, the scoring script and the
      full ground truth &mdash; class, CWE, root cause and smallest fix for each &mdash; are here:
      <a href="__REPO__">github.com/omarmohelal/sechelix-challenge</a></p>
      <p class="small">Built alongside <a href="__SECHELIX__">SecHelix</a>, an AppSec agent that
      sends every candidate finding to an independent verifier whose only job is to disprove it.
      The challenge is deliberately tool-neutral &mdash; nothing in it is SecHelix-specific.</p>
    </div>`));
  document.getElementById('quiz').innerHTML = '';
  r.scrollIntoView({behavior: 'smooth'});
}

render();
</script>
</body>
</html>
"""


def build() -> str:
    return (
        TEMPLATE.replace("__CASES__", json.dumps(build_cases(), indent=None))
        .replace("__REPO__", REPO)
        .replace("__SECHELIX__", SECHELIX)
    )


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(TRUTH)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
