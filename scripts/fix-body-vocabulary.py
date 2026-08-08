#!/usr/bin/env python3
"""
fix-body-vocabulary.py — one-shot backfill for posts whose article body uses
class names css/blog.css does not define.

Background (2026-08-08): alex-blog-draft.sh emitted devops.gheware.com's body
vocabulary — main.blog-post / article.post-content / div.post-header /
p.post-intro / div.cta-box / div.post-tags / span.tag. None of those selectors
exists in this site's stylesheets, so the posts rendered as full-bleed unstyled
text under a correct header. scripts/validate-template.py could not see it: it
asserted only that a stylesheet was linked and the template loader was present.

A second family (the 2026/05 backfill) carries a hero copy-pasted from
"Stop Wasting Doctor Visits" — wrong title, wrong background image — followed
by a bare <article> with no wrapper class at all.

This script rewrites both families to the pattern the rest of the corpus uses
and blog.css actually styles:

    <section class="blog-post-hero"> … title / category / date / read-time … </section>
    <article class="blog-post-content">
      <div class="container"> … body … </div>
    </article>

Usage:
  fix-body-vocabulary.py --dry-run [file ...]
  fix-body-vocabulary.py [file ...]        # rewrite in place
With no files, operates on every offender validate-template.py reports.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[1]

# Body wrappers that carry their own styling — these posts are fine as-is.
SELF_STYLED_RE = re.compile(r"<style[\s>]|style=\"[^\"]*max-width")

CLASS_MAP = {
    "post-intro": "lead",
    "cta-box": "blog-cta",
    "btn-primary": "blog-cta-button",
    "post-tags": "blog-post-tags",
    "tag": "blog-post-tag",
}

CATEGORY_ICON = "🩺"


def jsonld(soup):
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (ValueError, TypeError):
            continue
        for obj in data if isinstance(data, list) else [data]:
            if isinstance(obj, dict) and obj.get("@type") in ("BlogPosting", "Article"):
                return obj
    return {}


def human_date(iso):
    from datetime import date

    try:
        y, m, d = (int(x) for x in iso.split("T")[0].split("-"))
        return date(y, m, d).strftime("%B %-d, %Y")
    except (ValueError, AttributeError):
        return iso or ""


def parse_human_date(text):
    """'May 19, 2026' / 'May 3, 2026' -> '2026-05-19'."""
    from datetime import datetime

    m = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})", text or "")
    if not m:
        return ""
    try:
        return datetime.strptime(" ".join(m.groups()), "%B %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""


def extract_meta(soup, ld):
    """Title, category, ISO date, human date, read-time — from whichever
    element this post's family happens to carry them in.

    The in-body <h1> and meta row win over JSON-LD: the 2026/05 family's
    JSON-LD was written by an earlier backfill and carries a truncated
    headline ('… Premier…') plus one shared datePublished for every post,
    while the body carries each post's real title and date.
    """
    title = ""
    for h1 in soup.find_all("h1"):
        if "blog-post-hero-title" not in (h1.get("class") or []):
            title = h1.get_text(" ", strip=True)
            break
    if not title or title.endswith("…"):
        title = ld.get("headline") or title
    if not title and soup.title:
        title = soup.title.get_text(strip=True).split(" — ")[0]

    iso = ""
    header = soup.find(class_="post-header") or soup.find(class_="post-meta")
    if header is not None:
        t = header.find("time")
        if t and t.get("datetime"):
            iso = t["datetime"].split("T")[0]
        else:
            iso = parse_human_date(header.get_text(" ", strip=True))
    if not iso:
        iso = (ld.get("datePublished") or "").split("T")[0]

    category = ""
    el = soup.find(class_="post-category") or soup.select_one(".post-meta .tag")
    if el:
        category = el.get_text(" ", strip=True)
    if not category:
        category = ld.get("articleSection") or ""

    read = ""
    el = soup.find(class_="post-read-time")
    if el:
        read = el.get_text(" ", strip=True)
    if not read:
        for span in soup.select(".post-meta span, .post-header span"):
            txt = span.get_text(" ", strip=True)
            if "min read" in txt:
                read = txt
                break
    m = re.search(r"(\d+)\s*min read", read or "")
    read = f"{m.group(1)} min read" if m else read

    return title.strip(), category.strip(), iso, human_date(iso), read.strip()


def find_body_container(soup):
    """The element wrapping the article body, for each known family."""
    # main.blog-post first: it is the outermost wrapper of the generator
    # family, and .blog-post is itself undefined in blog.css — leaving it
    # behind would just be cruft around the replacement.
    return (
        soup.find("main", class_="blog-post")
        or soup.find("article", class_="post-content")
        or soup.find("article")
    )


STOP_IDS = {
    "author-bio-placeholder",
    "disclaimer-placeholder",
    "footer-placeholder",
}


def collect_loose_body(soup):
    """Body content that sits directly under <body>, between the hero and the
    template placeholders, with no wrapper element of its own."""
    hero = soup.find("section", class_="blog-post-hero")
    if hero is None:
        return []
    nodes = []
    for node in hero.next_siblings:
        name = getattr(node, "name", None)
        if name in ("script", "footer"):
            break
        if name and node.get("id") in STOP_IDS:
            break
        nodes.append(node)
    return [n for n in nodes if getattr(n, "name", None) or str(n).strip()]


def build_hero(soup, title, category, dt_iso, dt_human, read, existing):
    """Rebuild the hero. Reuse an existing background image only when it is
    this post's own — the 2026/05 family all share one foreign image."""
    bg = ""
    if existing is not None:
        style = existing.get("style", "")
        if "share-health-data-hero" not in style:
            bg = style

    section = soup.new_tag("section")
    section["class"] = ["blog-post-hero"]
    if bg:
        section["style"] = bg
        section["role"] = "img"
        section["aria-label"] = title

    inner = soup.new_tag("div")
    inner["class"] = ["container", "blog-post-hero-content"]
    section.append(inner)

    crumb = soup.new_tag("div")
    crumb["class"] = ["blog-post-breadcrumb"]
    a = soup.new_tag("a", href="/blog")
    a["class"] = ["breadcrumb-link"]
    a.string = "← Back to Blog"
    crumb.append(a)
    inner.append(crumb)

    if category:
        badge = soup.new_tag("div")
        badge["class"] = ["blog-post-category-badge"]
        icon = soup.new_tag("span")
        icon["class"] = ["category-icon"]
        icon.string = CATEGORY_ICON
        badge.append(icon)
        badge.append(f" {category}")
        inner.append(badge)

    h1 = soup.new_tag("h1")
    h1["class"] = ["blog-post-hero-title"]
    h1.string = title
    inner.append(h1)

    meta = soup.new_tag("div")
    meta["class"] = ["blog-post-hero-meta"]
    items = []
    if dt_human:
        items.append(("📅", dt_human, dt_iso))
    if read:
        items.append(("⏱️", read, None))
    for idx, (icon_txt, label, iso) in enumerate(items):
        if idx:
            div = soup.new_tag("div")
            div["class"] = ["meta-divider"]
            div.string = "•"
            meta.append(div)
        item = soup.new_tag("div")
        item["class"] = ["meta-item"]
        ic = soup.new_tag("span")
        ic["class"] = ["meta-icon"]
        ic.string = icon_txt
        item.append(ic)
        if iso:
            val = soup.new_tag("time", datetime=iso)
        else:
            val = soup.new_tag("span")
        val.string = label
        item.append(val)
        meta.append(item)
    if items:
        inner.append(meta)

    return section


def remap_classes(root):
    for el in root.find_all(class_=True):
        el["class"] = [CLASS_MAP.get(c, c) for c in el.get("class")]


def convert(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    if SELF_STYLED_RE.search(raw):
        return False
    # Two files in the 2026/05 family open <body> twice.
    raw = re.sub(r"(<body>\s*){2,}", "<body>\n", raw, count=1)

    soup = BeautifulSoup(raw, "html.parser")
    if soup.find("article", class_="blog-post-content") is not None:
        return False  # already conforms — never wrap twice
    # A stray inner div.post-content (2026/04) carries no styling of its own.
    for d in soup.find_all("div", class_="post-content"):
        d.unwrap()
    ld = jsonld(soup)
    title, category, dt_iso, dt_human, read = extract_meta(soup, ld)
    if not title:
        print(f"  SKIP (no title): {path}", file=sys.stderr)
        return False

    container = find_body_container(soup)
    loose_nodes = None
    if container is None:
        # Two 2026/05 posts have no opening <article> at all — the body content
        # sits directly under <body> between the hero and the placeholders,
        # with a stray unmatched </article> further down.
        loose_nodes = collect_loose_body(soup)
        if not loose_nodes:
            print(f"  SKIP (no body container): {path}", file=sys.stderr)
            return False

    scope = container if container is not None else loose_nodes

    # Strip the in-body title + meta row; the hero carries both. In the
    # 2026/05 family the FOOTER tag list is also a div.post-meta — only the
    # first one is the header row; later ones become .blog-post-tags.
    seen_header = False
    for node in scope if isinstance(scope, list) else [scope]:
        if not hasattr(node, "find_all"):
            continue
        own = [node] if node.get("class") and "post-meta" in node["class"] else []
        for el in node.find_all(class_="post-header"):
            el.decompose()
        for el in own + node.find_all(class_="post-meta"):
            if not seen_header:
                seen_header = True
                el.decompose()
            else:
                el["class"] = ["blog-post-tags"]
                el.attrs.pop("style", None)
        if node.name == "h1" and "blog-post-hero-title" not in (node.get("class") or []):
            node.decompose()
            continue
        for h1 in node.find_all("h1"):
            if "blog-post-hero-title" not in (h1.get("class") or []):
                h1.decompose()

    if container is not None:
        inner = container.find("article", class_="post-content") or container
        body_nodes = list(inner.contents)
    else:
        body_nodes = [n for n in loose_nodes if getattr(n, "decomposed", False) is not True]

    new_article = soup.new_tag("article")
    new_article["class"] = ["blog-post-content"]
    wrapper = soup.new_tag("div")
    wrapper["class"] = ["container"]
    new_article.append(wrapper)
    anchor_point = body_nodes[0] if body_nodes else None
    if container is None and anchor_point is not None:
        anchor_point.insert_before(new_article)
    for node in body_nodes:
        wrapper.append(node.extract())
    remap_classes(new_article)

    old_hero = soup.find("section", class_="blog-post-hero")
    new_hero = build_hero(soup, title, category, dt_iso, dt_human, read, old_hero)

    if container is not None:
        container.replace_with(new_article)
    if old_hero is not None:
        old_hero.replace_with(new_hero)
    else:
        anchor = soup.find(id="header-placeholder")
        if anchor is not None:
            anchor.insert_after(new_hero)
        else:
            new_article.insert_before(new_hero)

    path.write_text(str(soup), encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        sys.path.insert(0, str(REPO / "scripts"))
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "vt", REPO / "scripts" / "validate-template.py"
        )
        vt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vt)
        targets = [
            p
            for p in sorted((REPO / "posts").rglob("*.html"))
            if not vt.is_redirect_stub(p.read_text(encoding="utf-8", errors="replace"))
            and vt.missing(p.read_text(encoding="utf-8", errors="replace"))
        ]

    print(f"{len(targets)} post(s) to convert")
    changed = 0
    for path in targets:
        if args.dry_run:
            print(f"  would convert {path.resolve().relative_to(REPO)}")
            continue
        if convert(path):
            changed += 1
            print(f"  converted {path.resolve().relative_to(REPO)}")
    if not args.dry_run:
        print(f"{changed} converted")


if __name__ == "__main__":
    main()
