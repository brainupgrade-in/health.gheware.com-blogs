#!/usr/bin/env python3
"""Fix meta description + internal links in BeatO CGM post."""
import re

path = 'health.gheware.com-blogs/posts/2026/05/beato-cgm-3999-review-india-2026.html'
with open(path) as f:
    html = f.read()

# Fix meta descriptions (must be 120-170 chars)
new_desc = "BeatO CGM ₹3,999 reviewed vs Abbott Libre and Ultrahuman M1. We test real-world accuracy for Indian diabetics in 2026. 7-point comparison inside."
print(f"Meta description length: {len(new_desc)} chars")

html = re.sub(
    r'(<meta\s+content=")[^"]*("(?:\s+name="description"|property="og:description"|name="twitter:description"))',
    rf'\1{new_desc}\2',
    html
)

# Fix JSON-LD description
html = re.sub(
    r'"description":\s*"[^"]*"',
    f'"description": "{new_desc}"',
    html
)

# Fix internal links: ../../2026/04/xxx -> /blog/posts/2026/04/xxx
html = re.sub(
    r'href="\.\./\.\./(\d{4})/(\d{2})/([^"]+)"',
    r'href="/blog/posts/\1/\2/\3"',
    html
)

with open(path, 'w') as f:
    f.write(html)

print("Done. File updated.")
