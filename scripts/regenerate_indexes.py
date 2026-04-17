#!/usr/bin/env python3
"""Regenerate posts.json, sitemap.xml, and feed.xml from posts/*.html.

This is the single source of truth. The HTML files ARE the blog; these index
artefacts are derived. Run this after creating/editing/deleting any post.

Called by scripts/publish.sh and by .github/workflows/validate-indexes.yml
(the CI drift check). If you add a new field to posts.json, update
normalize_entry() here AND index.html's render code together.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "posts"
JSON_PATH = REPO / "posts.json"
SITEMAP_PATH = REPO / "sitemap.xml"
FEED_PATH = REPO / "feed.xml"

BASE = "https://health.gheware.com/blog"

# --- Category taxonomy ---------------------------------------------------------
# Canonical slug -> display label. The renderer (index.html) iterates category
# counts from posts and looks up icons in its own categoryConfig table. Adding
# a new slug here without also adding it to index.html's categoryConfig falls
# back to a generic icon, which is fine.
CATEGORY_LABEL = {
    "ai-health-tech": "Technology & AI",
    "awareness": "Prevention & Awareness",
    "complications": "Complications",
    "diabetes-management": "Diabetes Management",
    "diagnosis": "Testing & Diagnosis",
    "diet-nutrition": "Diet & Nutrition",
    "fitness-diabetes": "Exercise & Fitness",
    "medications": "Medication & Treatment",
    "medicines-treatments": "Medicines & Treatments",
    "mental-health": "Mental Health",
    "nutrition-lifestyle": "Diet & Nutrition",
    "research": "Research",
    "seasonal-care": "Seasonal Care",
    "sleep-health": "Sleep & Lifestyle",
    "treatment-management": "Treatment & Management",
}

# Normalize whatever string appears in article:section or `category` to a
# canonical slug. Keys are lowercased + html-unescaped. Anything not here that
# is also not already a canonical slug becomes a kebab-cased version of itself.
CATEGORY_ALIASES = {
    # diabetes management / blood sugar
    "diabetes management": "diabetes-management",
    "blood sugar management": "diabetes-management",
    "health & diabetes": "diabetes-management",
    # nutrition (all variants collapse here)
    "diet & nutrition": "nutrition-lifestyle",
    "diet-nutrition": "nutrition-lifestyle",
    "nutrition & diet": "nutrition-lifestyle",
    "nutrition": "nutrition-lifestyle",
    "nutrition & lifestyle": "nutrition-lifestyle",
    "lifestyle & wellness": "nutrition-lifestyle",
    # complications
    "complications": "complications",
    "complications-care": "complications",
    "complications & care": "complications",
    "complications & prevention": "complications",
    "diabetes complications": "complications",
    "comorbidities": "complications",
    # medications
    "medications": "medications",
    "diabetes medications": "medications",
    "medicine & treatment": "medications",
    "medication & treatment": "medications",
    "medicines & treatments": "medications",
    # treatment programs
    "treatment & management": "treatment-management",
    # seasonal
    "seasonal care": "seasonal-care",
    # tech
    "ai & health tech": "ai-health-tech",
    "technology & ai": "ai-health-tech",
    "technology & devices": "ai-health-tech",
    "diabetes technology": "ai-health-tech",
    # sleep, fitness, mental
    "sleep & health": "sleep-health",
    "sleep & lifestyle": "sleep-health",
    "fitness & diabetes": "fitness-diabetes",
    "exercise & fitness": "fitness-diabetes",
    "exercise & activity": "fitness-diabetes",
    "exercise-lifestyle": "fitness-diabetes",
    "exercise & lifestyle": "fitness-diabetes",
    "mental health": "mental-health",
    # diagnosis
    "diagnosis": "diagnosis",
    "testing & diagnosis": "diagnosis",
    "diabetes testing/monitoring": "diagnosis",
    "diabetes testing-monitoring": "diagnosis",
    "diabetes testing & monitoring": "diagnosis",
    # awareness / prevention
    "awareness": "awareness",
    "diabetes awareness": "awareness",
    "prevention": "awareness",
    "prevention & awareness": "awareness",
    "understanding diabetes": "awareness",
    # emergencies
    "diabetes emergencies": "emergencies",
    # research
    "research": "research",
    "diabetes research": "research",
    # tutorials / how-to
    "tutorial": "tutorials",
    "tutorials": "tutorials",
    "app installation guide": "tutorials",
    # education / misc
    "health education": "health-education",
}


def canonical_category(raw):
    if not raw:
        return "diabetes-management"
    # Unescape HTML entities first — article:section values arrive as either
    # "Diet & Nutrition" or "Diet &amp; Nutrition" across the corpus.
    key = html_unescape(raw).strip().lower()
    if key in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[key]
    if raw in CATEGORY_LABEL or key in CATEGORY_LABEL:
        return key if key in CATEGORY_LABEL else raw
    # Convert to kebab-case as fallback (drops & and other punctuation)
    slug = re.sub(r"[^a-z0-9]+", "-", key).strip("-")
    return slug or "diabetes-management"


def category_label(slug):
    if slug in CATEGORY_LABEL:
        return CATEGORY_LABEL[slug]
    return " ".join(w.capitalize() for w in slug.split("-"))


# --- HTML metadata extraction -------------------------------------------------
def extract_meta(html, attr, value):
    pat1 = rf'<meta\s+{attr}="{re.escape(value)}"\s+content="([^"]*)"'
    pat2 = rf'<meta\s+content="([^"]*)"\s+{attr}="{re.escape(value)}"'
    m = re.search(pat1, html) or re.search(pat2, html)
    return m.group(1) if m else None


def extract_meta_all(html, attr, value):
    pat1 = rf'<meta\s+{attr}="{re.escape(value)}"\s+content="([^"]*)"'
    pat2 = rf'<meta\s+content="([^"]*)"\s+{attr}="{re.escape(value)}"'
    return re.findall(pat1, html) + re.findall(pat2, html)


def html_unescape(s):
    if s is None:
        return s
    return (
        s.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&#x27;", "'")
    )


def xml_escape(s):
    if s is None:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def estimate_read_time(html):
    text = re.sub(r"<script[\s\S]*?</script>", " ", html)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    words = len(re.findall(r"\w+", text))
    return f"{max(5, round(words / 220))} min read"


def entry_for(path_rel, html, existing=None, next_id_ref=None):
    """Build a fully-populated entry for one post."""
    existing = existing or {}

    og_title = extract_meta(html, "property", "og:title")
    meta_title = extract_meta(html, "name", "title")
    title_tag = re.search(r"<title>([^<]+)</title>", html)
    title = html_unescape(
        (og_title or meta_title or (title_tag.group(1) if title_tag else "Untitled")).strip()
    )

    desc = extract_meta(html, "name", "description") or extract_meta(
        html, "property", "og:description"
    )
    desc = html_unescape(desc) if desc else existing.get("description", "")

    pub = extract_meta(html, "property", "article:published_time")
    if not pub:
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
        if m:
            pub = m.group(1)
    iso_date = pub[:10] if pub else existing.get("date", "2026-01-01")

    section = extract_meta(html, "property", "article:section") or existing.get("category", "")
    cat_slug = canonical_category(section)
    cat_label = category_label(cat_slug)

    keywords_str = extract_meta(html, "name", "keywords") or ""
    keywords = [k.strip() for k in keywords_str.split(",") if k.strip()] or existing.get(
        "keywords", []
    )

    tags = extract_meta_all(html, "property", "article:tag") or existing.get("tags", [])

    og_image = extract_meta(html, "property", "og:image")
    image = og_image or existing.get("image") or f"assets/images/{Path(path_rel).stem}-hero.jpg"

    read_time = existing.get("readTime") or estimate_read_time(html)

    post_id = existing.get("id")
    if post_id is None and next_id_ref is not None:
        post_id = next_id_ref[0]
        next_id_ref[0] += 1

    return {
        "id": post_id,
        "title": title,
        "slug": path_rel,
        "path": path_rel,
        "url": path_rel,
        "date": iso_date,
        "category": cat_slug,
        "categoryLabel": cat_label,
        "description": desc,
        "excerpt": desc,
        "keywords": keywords,
        "tags": tags,
        "image": image,
        "readTime": read_time,
        "featured": bool(existing.get("featured", False)),
    }


# --- Main ---------------------------------------------------------------------
def load_existing():
    if not JSON_PATH.exists():
        return {"posts": [], "categories": [], "postsPerPage": 12}
    with open(JSON_PATH) as f:
        return json.load(f)


def main():
    existing_doc = load_existing()
    existing_by_path = {}
    for p in existing_doc.get("posts", []):
        ref = p.get("slug") or p.get("path") or p.get("url") or ""
        ref = re.sub(r"^https?://[^/]+/blog/", "", ref)
        if ref:
            existing_by_path[ref] = p

    max_id = max((p.get("id") or 0) for p in existing_doc.get("posts", [])) or 0
    next_id = [max_id + 1]  # mutable ref for closure-style assignment

    entries = []
    for root, _, files in os.walk(POSTS_DIR):
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            full = Path(root) / f
            if full.stat().st_size == 0:
                print(f"  skip 0-byte: {full.relative_to(REPO)}", file=sys.stderr)
                continue
            rel = str(full.relative_to(REPO))
            html = full.read_text(encoding="utf-8")
            existing = existing_by_path.get(rel)
            entries.append(entry_for(rel, html, existing, next_id))

    # Sort: date desc, id desc as tiebreak
    entries.sort(key=lambda e: (e["date"], e.get("id") or 0), reverse=True)

    # Assign monotonic ids to any still-missing
    for e in entries:
        if e["id"] is None:
            e["id"] = next_id[0]
            next_id[0] += 1

    # Write posts.json preserving top-level keys
    out_doc = dict(existing_doc)
    out_doc["posts"] = entries
    JSON_PATH.write_text(
        json.dumps(out_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Write sitemap.xml
    newest = entries[0]["date"] if entries else "2026-01-01"
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          "  <url>",
          f"    <loc>{BASE}/</loc>",
          f"    <lastmod>{newest}</lastmod>",
          "    <changefreq>daily</changefreq>",
          "    <priority>1.0</priority>",
          "  </url>"]
    for p in entries:
        sm.append("  <url>")
        sm.append(f"    <loc>{BASE}/{p['slug']}</loc>")
        sm.append(f"    <lastmod>{p['date']}</lastmod>")
        sm.append("    <changefreq>monthly</changefreq>")
        sm.append("    <priority>0.8</priority>")
        sm.append("  </url>")
    sm.append("</urlset>")
    sm.append("")
    SITEMAP_PATH.write_text("\n".join(sm), encoding="utf-8")

    # Write feed.xml (RSS 2.0) — newest 50 posts
    # lastBuildDate uses the newest post's date (not wall-clock time) so that
    # running the regenerator twice on the same tree is a no-op. The CI drift
    # check relies on determinism.
    if entries:
        try:
            dt = datetime.strptime(entries[0]["date"], "%Y-%m-%d")
            now = dt.strftime("%a, %d %b %Y 00:00:00 +0000")
        except ValueError:
            now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    else:
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    feed = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            "  <channel>",
            "    <title>Health Gheware — Diabetes Management for Indians</title>",
            f"    <link>{BASE}/</link>",
            "    <description>Practical, evidence-based diabetes guides for Indian patients — nutrition, medication, CGM, HbA1c, complications, and seasonal care.</description>",
            "    <language>en-IN</language>",
            f"    <lastBuildDate>{now}</lastBuildDate>",
            f'    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>']
    for p in entries[:50]:
        # RFC-822 date from iso
        try:
            dt = datetime.strptime(p["date"], "%Y-%m-%d")
            pub_date = dt.strftime("%a, %d %b %Y 00:00:00 +0000")
        except ValueError:
            pub_date = now
        url = f"{BASE}/{p['slug']}"
        feed.append("    <item>")
        feed.append(f"      <title>{xml_escape(p['title'])}</title>")
        feed.append(f"      <link>{url}</link>")
        feed.append(f"      <guid>{url}</guid>")
        feed.append(f"      <description>{xml_escape(p.get('description',''))}</description>")
        feed.append(f"      <category>{xml_escape(p.get('categoryLabel',''))}</category>")
        feed.append("      <author>rajesh@gheware.com (Rajesh Gheware)</author>")
        feed.append(f"      <pubDate>{pub_date}</pubDate>")
        feed.append("    </item>")
    feed.append("  </channel>")
    feed.append("</rss>")
    feed.append("")
    FEED_PATH.write_text("\n".join(feed), encoding="utf-8")

    # Validate
    required = ("excerpt", "categoryLabel", "readTime", "category", "slug", "date", "title")
    missing = [
        (e["slug"], [k for k in required if not e.get(k)])
        for e in entries
        if not all(e.get(k) for k in required)
    ]
    if missing:
        print("ERROR: entries missing required fields:", file=sys.stderr)
        for slug, miss in missing:
            print(f"  {slug}: {miss}", file=sys.stderr)
        sys.exit(2)

    # Catch future-dated datePublished typos. A post stamped e.g. 2026-06-01
    # on 2026-03-05 pins the blog index for months until someone notices.
    # Hard fail so the agent/CI stops the push.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    future = [(e["slug"], e["date"]) for e in entries if e["date"] > today]
    if future:
        print(f"ERROR: {len(future)} post(s) have date in the future (today={today}):", file=sys.stderr)
        for slug, date in future:
            print(f"  {date}  {slug}", file=sys.stderr)
        print("Fix the article:published_time / JSON-LD datePublished in the post HTML.", file=sys.stderr)
        sys.exit(2)

    print(f"posts.json : {len(entries)} entries (newest {entries[0]['date']})")
    print(f"sitemap.xml: {len(entries) + 1} URLs")
    print(f"feed.xml   : {min(50, len(entries))} items")


if __name__ == "__main__":
    main()
