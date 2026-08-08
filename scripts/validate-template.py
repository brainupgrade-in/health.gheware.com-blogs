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
  (c) body classes — a post that relies on css/blog.css (i.e. has no inline
                     <style> of its own) must wrap its article in the class
                     name blog.css actually defines: .blog-post-content, which
                     is what every h2/h3/p/ul/a/blockquote rule is scoped under.

(a) and (b) only prove the CHROME renders; they say nothing about the body.
2026-08-08: 19 posts shipped carrying premium.css + blog.css + a valid
template-loader + all four placeholders and still rendered as unstyled
full-bleed text, because alex-blog-draft.sh emitted Dev's devops.gheware.com
vocabulary (post-content / post-header / post-intro / cta-box / post-tags) —
none of which exists in Alex's blog.css. Every one passed this gate. A
conformance gate must assert the selectors the body depends on, not just the
<link> that loads them.

Skipped: http-equiv="refresh" redirect stubs. Check (c) is additionally
skipped for posts carrying their own inline <style> block — the legacy
self-styled family does not depend on blog.css, so its vocabulary
does not apply.

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
# A post is "self-styled" — and therefore exempt from (c) — if it carries its
# own <style> block, or wraps its body in an element that sets its own measure
# via a style= attribute. Both legacy families do one or the other; neither
# depends on blog.css's vocabulary.
INLINE_STYLE_RE = re.compile(r"<style[\s>]|style=\"[^\"]*max-width")
# .blog-post-content is what css/blog.css uses to style the article body —
# every h2/h3/p/ul/li/a/blockquote/code rule is scoped under it. Without this
# wrapper the body inherits nothing and renders as full-bleed unstyled text.
BODY_CLASS_RES = {
    "blog-post-content": re.compile(r"class=\"[^\"]*\bblog-post-content\b"),
}
# Dev's devops.gheware.com vocabulary — valid there, undefined in Alex's blog.css.
FOREIGN_CLASS_RE = re.compile(
    r"class=\"(?:post-content|post-header|post-intro|post-tags|cta-box)\""
)


def is_redirect_stub(text: str) -> bool:
    return 'http-equiv="refresh"' in text


def missing(text: str):
    miss = []
    if not STYLE_RE.search(text):
        miss.append("styling(<style>|stylesheet)")
    if not TEMPLATE_RE.search(text):
        miss.append("template-loader")
    # (c) only applies to posts that depend on the shared blog.css.
    if not INLINE_STYLE_RE.search(text):
        for name, rx in BODY_CLASS_RES.items():
            if not rx.search(text):
                miss.append(f"body-class(.{name})")
        if FOREIGN_CLASS_RE.search(text):
            miss.append("foreign-body-classes(devops.gheware.com vocabulary)")
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
            "so header/footer/author-bio/disclaimer render. See scripts/publish.sh STEP 0.\n"
            "\nbody-class/foreign-body-classes: the article body must use the class\n"
            "names css/blog.css defines, or it renders unstyled under a correct header:\n"
            '  <article class="blog-post-content"><div class="container"> … </div></article>\n'
            "with .blog-post-hero for the title block and .blog-post-tags / .blog-cta.\n"
            "Do NOT copy devops.gheware.com's post-content / post-header / post-intro /\n"
            "cta-box / post-tags — those selectors do not exist in this site's stylesheets.",
            file=sys.stderr,
        )
        return 1

    print(f"Template conformance OK — {checked} post(s) conform.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
