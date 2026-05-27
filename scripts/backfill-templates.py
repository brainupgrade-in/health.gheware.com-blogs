#!/usr/bin/env python3
"""Backfill May 2026 posts with full template from reference."""
import re
import os
from pathlib import Path
import sys

os.chdir('/home/openclaw/.openclaw/workspace')

# Read reference template
ref = open('/tmp/ref-template.html').read()

# Split into parts
m = re.search(r'<article[^>]*>', ref)
if not m:
    print('ERROR: No article tag in reference'); sys.exit(1)

article_open = m.group(0)
article_close = '</article>'
end = ref.find(article_close, m.start())

head_with_body = ref[:m.start()]  # everything before <article...
after_article = ref[end + len(article_close):]  # closing tags + </body></html>

print(f'Head+body+hero: {len(head_with_body)} chars')
print(f'After article: {len(after_article)} chars')

# Process May 2026 posts
posts_dir = Path('health.gheware.com-blogs/posts/2026/05')
skipped = 'beato-cgm-3999-review-india-2026.html'
results = []

for post_file in sorted(posts_dir.glob('*.html')):
    fname = post_file.name
    if fname == skipped:
        print(f'SKIP (already fixed): {fname}')
        continue
    
    post_html = post_file.read_text()
    
    # Extract existing article body
    article_match = re.search(r'<article[^>]*>(.*?)</article>', post_html, re.DOTALL)
    if not article_match:
        print(f'  FAIL: No article tag in {fname}')
        continue
    
    article_body = article_match.group(0)
    
    # New HTML = head+body+hero + article_body + after_article
    new_html = head_with_body + article_body + after_article
    
    # Validate
    wc_match = re.sub(r'<[^>]+>', ' ', article_body)
    wc = len(wc_match.split())
    
    title_m = re.search(r'<title>([^<]+)</title>', new_html)
    title = title_m.group(1) if title_m else ''
    
    results.append({
        'file': fname,
        'words': wc,
        'title': title,
        'title_len': len(title),
    })
    
    # Write
    post_file.write_text(new_html)
    print(f'  {fname}: {wc} words, title={len(title)} chars')

# Summary
print(f'\nProcessed: {len(results)} posts')
all_ok = all(1500 <= r['words'] <= 4500 and r['title_len'] <= 65 for r in results)
print(f'All gates pass: {all_ok}')
for r in results:
    wc_ok = 1500 <= r['words'] <= 4500
    tl_ok = r['title_len'] <= 65
    print(f"  {'OK' if wc_ok and tl_ok else '!!'} {r['file']}: {r['words']}w, title {r['title_len']}c")
