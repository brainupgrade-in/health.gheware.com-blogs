#!/usr/bin/env python3
"""Fix meta descriptions >170 chars across all backfilled posts."""
import re, os

os.chdir('/home/openclaw/.openclaw/workspace')
posts_dir = 'health.gheware.com-blogs/posts/2026/05'

for fname in sorted(os.listdir(posts_dir)):
    if not fname.endswith('.html'):
        continue

    fpath = os.path.join(posts_dir, fname)
    with open(fpath) as f:
        html = f.read()

    # Find all meta tags with content + description/og:description/twitter:description
    def fix_meta(m):
        content = m.group(1)
        suffix = m.group(2)
        if len(content) <= 170:
            return m.group(0)
        t = content[:167]
        last_space = max(t.rfind(' '), t.rfind('—'), t.rfind('-'))
        new_content = t[:max(last_space, 120)] + '...'
        return f'content="{new_content}"{suffix}'

    html = re.sub(
        r'content="([^"]{171,})"((?:\s+name="description"|property="og:description"|name="twitter:description")\s*/?>)',
        fix_meta,
        html
    )

    with open(fpath, 'w') as f:
        f.write(html)

    # Verify
    meta_matches = re.findall(r'content="([^"]{120,})"(?:\s+name="description"|property="og:description"|name="twitter:description")', html)
    max_len = max(len(m) for m in meta_matches) if meta_matches else 0
    print(f"  {fname}: meta max={max_len} chars")

print("Done!")
