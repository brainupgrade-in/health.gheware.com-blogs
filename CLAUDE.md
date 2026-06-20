# health.gheware.com-blogs

Static GitHub Pages site for Alex's diabetes-management blog.
Live: https://health.gheware.com/blog (proxied — root domain is a separate SPA).

## Layout

- `posts/{YYYY}/{MM}/*.html` — blog post sources (the source of truth)
- `posts.json`, `sitemap.xml`, `feed.xml` — **derived**; never hand-edit
- `assets/{images,pdfs,videos}/` — hero images, lead-magnet PDFs, embedded videos
- `templates/{header,footer,author-bio,disclaimer}.html` — shared chrome, loaded at
  runtime by `js/template-loader.js` (injects header→`<body>` top, footer→bottom,
  fills `#author-bio-placeholder` + `#disclaimer-placeholder` if present). **Self-styling:**
  each partial carries its own `<style>` — `.header-compact`/`.footer-compact`/`.disclaimer-compact`
  are in NO `css/` file, so a post needs no css-trio to style the template chrome.
  Every post MUST load `template-loader.js` (or render with no header/footer/disclaimer).
- `css/`, `js/` — site-wide stylesheets + scripts
- `scripts/` — publish pipeline (symlinked from `docs/scripts/`)
- 25 standalone HTML pages at root (about, lead-magnet landing pages, guides)

## Publishing flow

```bash
# Edit or add posts/YYYY/MM/your-slug.html, then:
scripts/publish.sh "commit message"
```

`publish.sh` runs the template-scaffolding guard, regenerates `posts.json` /
`sitemap.xml` / `feed.xml` from disk, commits, pushes, and pings Google
Indexing API + IndexNow + Yandex.

If editing in this repo without the agent toolchain (no Google service
account, no Python at the openclaw path), just run:

```bash
python3 scripts/regenerate_indexes.py && git add -A && git commit && git push
```

CI workflow `.github/workflows/validate-indexes.yml` fails any push where
`posts.json` / `sitemap.xml` / `feed.xml` drift from what
`regenerate_indexes.py` produces from `posts/*.html`.

## Template-conformance gate (2026-06-20)

`scripts/validate-template.py` fails any post that lacks **(a)** site styling
(`<style>` or a stylesheet `<link>`) **or (b)** a template loader
(`template-loader.js`, or legacy `function loadTemplate` / inline
`fetch('…/templates/…')`) — i.e. would render with no header/footer/author-bio/
disclaimer. Enforced at **3 layers**: `publish.sh` STEP 0, the repo-local
**pre-commit** hook (install via `scripts/install-hooks.sh`), and CI
`.github/workflows/validate-template.yml`. Run standalone:
`python3 scripts/validate-template.py` (whole tree) or pass specific files.

Backstops the 2026-06 drift where 27 posts shipped with bespoke inline chrome
instead of the template (all converted + render-verified). **Verify rendering**
with a real browser, not just grep: `python3 -m http.server 8099` in repo root,
then `google-chrome-stable --headless --dump-dom http://localhost:8099/posts/…`,
parse with `bs4`, assert exactly 1 each of `header.header-compact` /
`footer.footer-compact` / `.author-bio` / `.disclaimer-compact`. (Note: a
post-title `<header class="post-header"|"hero">` and an in-article
`<nav class="toc">` are CONTENT, not chrome — never strip them.)

> Running `publish.sh` on the owner machine (not the agent pod)? Its `$PYTHON`
> is hardcoded to the pod path — call with `PYTHON=/usr/bin/python3`, or just do
> `python3 scripts/regenerate_indexes.py && git commit && git push` manually.

## Hero image source-of-truth

Each post HTML carries `<meta property="og:image" content="...">`.
`regenerate_indexes.py` reads it and stores it in `posts.json`. The blog
index page (`https://health.gheware.com/blog/`) renders `post.image` directly
as `<img src>`. So:

- To change a post's hero, edit the `og:image` URL in that post's HTML
  (also update `twitter:image` and the JSON-LD `image` field for consistency)
- The og:image filename MUST exist on disk (otherwise live index shows
  broken hero — silently passes CI). Inventory lives at `assets/images/*.jpg`.

## Hard rules

- Never commit `posts.json` / `sitemap.xml` / `feed.xml` edits unless they
  came from `regenerate_indexes.py`.
- Every post HTML needs the CSS trio (`../../../css/{critical,blog,responsive}.css`)
  OR an inline `<style>` block — `publish.sh`'s template-scaffolding guard
  refuses to publish posts without it.
- Use `docs/scripts/...` and `scripts/...` interchangeably — `docs/scripts`
  is a symlink to `../scripts`, kept for documentation discoverability.
- `.nojekyll` is intentional (this is a non-Jekyll Pages site). Don't delete.
- **No video files in this repo.** `assets/videos/`, `*.mp4`, `*.webm`,
  `*.mov` are gitignored. Reels publish to YouTube Shorts (canonical
  permanent host) via the YouTube Data API; FB and IG posts then attach
  the YouTube URL as a link share (FB renders a link card; IG places it
  in caption text). Native IG/FB Reels would require a real video CDN —
  intentionally deferred. If you need a temporary URL for any other
  purpose, use `video-service`'s `/files/<jobId>/<file>.mp4` endpoint
  (24h TTL on the PVC) — never the blog repo.

## Operational context

This repo is also cloned onto Alex's PVC at
`~/.openclaw/workspace/health.gheware.com-blogs`. After any owner-side push
to `main`, Alex must `git pull` to sync — otherwise stale clones can
"resurrect" old content via routine cron pushes. See gotcha
`feedback_unpublish_resurrection` in the parent ai-business-agents repo.

Full operational rules + agent context live at
`~/ai-business-agents/CLAUDE.md`.
