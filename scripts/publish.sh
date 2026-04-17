#!/bin/bash
# =============================================================================
# UNIFIED BLOG PUBLISH SCRIPT
# Run after creating a new blog post to handle all publishing steps.
# Usage: ./scripts/publish.sh "Commit message" [url1] [url2] ...
# If no URLs provided, auto-detects new/modified post files from git status.
# =============================================================================

set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

PYTHON="/home/openclaw/.openclaw/.local/python/cpython-3.12.10-linux-x86_64-gnu/bin/python3.12"
BLOG_BASE="https://health.gheware.com/blog"
SA_FILE="/home/openclaw/.openclaw/workspace/google-service-account.json"

COMMIT_MSG="${1:-Auto-publish blog update}"
shift 2>/dev/null || true

echo "=========================================="
echo "📝 BLOG PUBLISH PIPELINE"
echo "=========================================="

# ─── STEP 1: Regenerate posts.json + sitemap.xml + feed.xml from disk ─────────
# The HTML files in posts/ are the source of truth. This rebuilds every index
# so posts.json can never drift from what is actually on disk. See
# scripts/regenerate_indexes.py for the logic (category taxonomy lives there).
echo ""
echo "1️⃣  Regenerating posts.json + sitemap.xml + feed.xml from disk..."
$PYTHON scripts/regenerate_indexes.py

# ─── STEP 2: Git commit & push ───────────────────────────────────────────────
echo ""
echo "2️⃣  Git commit & push..."
git add -A
git commit -m "$COMMIT_MSG" 2>/dev/null && echo "   ✅ Committed: $COMMIT_MSG" || echo "   ℹ️  Nothing new to commit"
git push origin main 2>&1 | tail -2
echo "   ✅ Pushed to GitHub Pages"

# ─── STEP 3: Collect URLs to submit ──────────────────────────────────────────
URLS=("$@")
if [ ${#URLS[@]} -eq 0 ]; then
    echo ""
    echo "3️⃣  Auto-detecting new/modified post URLs..."
    # Get recently committed HTML files
    while IFS= read -r file; do
        if [[ "$file" == posts/*.html ]]; then
            URLS+=("${BLOG_BASE}/${file}")
        fi
    done < <(git diff --name-only HEAD~1 HEAD -- 'posts/*.html' 2>/dev/null)
fi

if [ ${#URLS[@]} -eq 0 ]; then
    echo "   ℹ️  No new post URLs detected. Skipping indexing."
else
    echo "   Found ${#URLS[@]} URLs to submit"

    # ─── STEP 4: Google Indexing API ──────────────────────────────────────────
    echo ""
    echo "4️⃣  Google Indexing API..."
    $PYTHON << PYEOF
from google.oauth2 import service_account
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/indexing']
creds = service_account.Credentials.from_service_account_file('$SA_FILE', scopes=SCOPES)
service = build('indexing', 'v3', credentials=creds)
urls = """$(printf '%s\n' "${URLS[@]}")""".strip().split('\n')
for url in urls:
    url = url.strip()
    if not url: continue
    try:
        service.urlNotifications().publish(body={"url": url, "type": "URL_UPDATED"}).execute()
        print(f"   ✅ Google: {url.split('/')[-1]}")
    except Exception as e:
        print(f"   ❌ Google: {url.split('/')[-1]} — {e}")
PYEOF

    # ─── STEP 5: IndexNow (Bing, Yandex, Naver) ─────────────────────────────
    echo ""
    echo "5️⃣  IndexNow (Bing/Yandex)..."
    $PYTHON scripts/indexnow_submit.py "${URLS[@]}"

    # ─── STEP 6: Yandex sitemap ping ─────────────────────────────────────────
    echo ""
    echo "6️⃣  Yandex sitemap ping..."
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://yandex.com/ping?sitemap=${BLOG_BASE}/sitemap.xml" --max-time 10)
    echo "   Yandex ping: HTTP $STATUS"
fi

# ─── STEP 7: Report to agentgrow.io ──────────────────────────────────────────
echo ""
echo "7️⃣  Report to agentgrow.io..."
# This step is manual — caller should report with specific title/summary
echo "   ℹ️  Remember to report to agentgrow.io with category and module_key"

echo ""
echo "=========================================="
echo "✅ PUBLISH PIPELINE COMPLETE"
echo "=========================================="
echo "Submitted ${#URLS[@]} URLs to: Google Indexing API, IndexNow (Bing/Yandex), Yandex Sitemap Ping"
