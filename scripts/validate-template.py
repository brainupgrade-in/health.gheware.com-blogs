#!/usr/bin/env python3
"""
validate-template.py — blog-post template conformance gate.

Fails if any post ships without (a) site styling and (b) the shared template
loader, i.e. would render with no header/footer/author-bio/medical-disclaimer.
This is the standalone form of scripts/publish.sh STEP 0, reused by the
pre-commit hook and the validate-template GitHub Action so off-template drift
cannot recur for any author. (2026-06-20: 27 posts had shipped with bespoke
inline chrome instead of the template — all converted + render-verified.)

Required, per post:
  (a) styling      — an inline <style> block OR a <link rel="stylesheet">
  (b) template     — template-loader.js  (the standard), OR a legacy
                     `function loadTemplate`  OR inline `fetch('…/templates/…')`

Skipped: http-equiv="refresh" redirect stubs.

Usage:
  validate-template.py                 # scan every posts/**/*.html
  validate-template.py <file.html> ... # check only the given files (pre-commit)

Exit code: 0 if all conform, 1 otherwise.
"""

import re
import sys
from pathlib import Path

STYLE_RE = re.compile(r"<style[\s>]|<link[^>]+rel=\"stylesheet\"")
TEMPLATE_RE = re.compile(r"template-loader\.js|function loadTemplate|fetch\([^)]*templates/")


def is_redirect_stub(text: str) -> bool:
    return 'http-equiv="refresh"' in text


def missing(text: str):
    miss = []
    if not STYLE_RE.search(text):
        miss.append("styling(<style>|stylesheet)")
    if not TEMPLATE_RE.search(text):
        miss.append("template-loader")
    return miss


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    args = [a for a in sys.argv[1:]]
    if args:
        files = [Path(a) for a in args if a.endswith(".html")]
    else:
        files = sorted((repo_root / "posts").rglob("*.html"))

    offenders = []
    checked = 0
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_redirect_stub(text):
            continue
        checked += 1
        miss = missing(text)
        if miss:
            offenders.append((str(path), miss))

    if offenders:
        print("Template conformance check FAILED — non-conforming posts:\n", file=sys.stderr)
        for name, miss in offenders:
            print(f"  {name} -->{''.join(' ' + m for m in miss)}", file=sys.stderr)
        print(
            "\nEvery post needs site styling AND must load the shared template.\n"
            "Add before </body>:\n"
            '  <script defer src="../../../js/template-loader.js"></script>\n'
            "so header/footer/author-bio/disclaimer render. See scripts/publish.sh STEP 0.",
            file=sys.stderr,
        )
        return 1

    print(f"Template conformance OK — {checked} post(s) conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
