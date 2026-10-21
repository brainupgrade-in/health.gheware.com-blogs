#!/usr/bin/env python3
"""One-off (2026-10-21): point blog links that lead to the GlucoRay APP at https://glucoray.com.

Spec: health repo docs/specs/glucoray-primary-domain, T21 / AC-13. The app moved to glucoray.com;
health.gheware.com now 301s app pages there, so these links work either way, this just drops the hop.

Rewritten (only inside href="..."): https://health.gheware.com followed by nothing, "/", or
/privacy, /terms, /downloads/, /download-apk, /auth/..., /dashboard, /billing, /support
(optionally followed by ?query or #fragment).
NOT touched: /blog/* URLs, canonicals, og:image / JSON-LD / favicon URLs, sitemap.xml, feed.xml,
posts.json, the IndexNow host, and the non-app paths /about and /images/* (reported only).

Also replaces the hard-coded GA4 snippet for G-YZCBQZJFEM (2 posts) with the shared
js/analytics-loader.js (G-3345N5ZH75), so those posts join the cross-domain GA4 setup.

Usage: python3 scripts/rewrite_app_links_glucoray.py [--dry-run]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_HREF = re.compile(
    r'href="https://health\.gheware\.com'
    r'(/(?:privacy|terms|downloads/|download-apk|auth/[^"?#]*|dashboard|billing|support))?/?'
    r'((?:[?#][^"]*)?)"'
)
OLD_GA = re.compile(
    r'<!-- Google Analytics -->\n'
    r'<script async src="https://www\.googletagmanager\.com/gtag/js\?id=G-YZCBQZJFEM"></script>\n'
    r'<script>\n'
    r'window\.dataLayer = window\.dataLayer \|\| \[\];\n'
    r'function gtag\(\)\{dataLayer\.push\(arguments\);\}\n'
    r"gtag\('js', new Date\(\)\);\n"
    r"gtag\('config', 'G-YZCBQZJFEM'\);\n"
    r'</script>\n'
)
NEW_GA = '<!-- Google Analytics -->\n<script defer src="../../../js/analytics-loader.js"></script>\n'
SKIP_DIRS = {".git", "node_modules"}
DERIVED = {"sitemap.xml", "feed.xml", "posts.json"}


def rewrite(text):
    text, n_links = APP_HREF.subn(lambda m: f'href="https://glucoray.com{m.group(1) or "/"}{m.group(2)}"', text)
    text, n_ga = OLD_GA.subn(NEW_GA, text)
    return text, n_links, n_ga


def main():
    dry = "--dry-run" in sys.argv
    total_links = total_ga = files = 0
    for path in sorted(ROOT.rglob("*.html")):
        if SKIP_DIRS & set(path.parts) or path.name in DERIVED:
            continue
        old = path.read_text(encoding="utf-8")
        new, n_links, n_ga = rewrite(old)
        if new != old:
            files += 1
            total_links += n_links
            total_ga += n_ga
            print(f"{path.relative_to(ROOT)}: {n_links} link(s){f', GA4 fixed' if n_ga else ''}")
            if not dry:
                path.write_text(new, encoding="utf-8")
    print(f"{'would change' if dry else 'changed'} {files} file(s): {total_links} app link(s), {total_ga} GA4 snippet(s)")


if __name__ == "__main__":
    main()
