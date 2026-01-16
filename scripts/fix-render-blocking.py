#!/usr/bin/env python3
"""
Fix render-blocking resources in all blog posts.

Changes:
1. Add defer to analytics-loader.js
2. Load CSS asynchronously using media="print" onload pattern
3. Add defer to template-loader.js
4. Add preload for critical CSS
"""

import os
import re
from pathlib import Path

def fix_render_blocking(html_content):
    """Fix render-blocking resources in HTML content."""

    # 1. Add defer to analytics-loader.js (preserve full path)
    html_content = re.sub(
        r'<script src="((?:\.\./)+)js/analytics-loader\.js"></script>',
        r'<script defer src="\1js/analytics-loader.js"></script>',
        html_content
    )

    # 2. Change CSS loading to async pattern with preload
    # Pattern for CSS block (capture the full relative path)
    css_pattern = r'''<!-- CSS -->
    <link rel="stylesheet" href="((?:\.\./)+)css/premium\.css">
    <link rel="stylesheet" href="(?:\.\./)+css/blog\.css">
    <link rel="stylesheet" href="(?:\.\./)+css/responsive\.css">'''

    def css_replacement(match):
        prefix = match.group(1)
        return f'''<!-- Critical CSS Preload -->
    <link rel="preload" href="{prefix}css/critical.css" as="style">

    <!-- CSS (async loaded for non-blocking render) -->
    <link rel="stylesheet" href="{prefix}css/critical.css">
    <link rel="stylesheet" href="{prefix}css/premium.css" media="print" onload="this.media='all'">
    <link rel="stylesheet" href="{prefix}css/blog.css" media="print" onload="this.media='all'">
    <link rel="stylesheet" href="{prefix}css/responsive.css" media="print" onload="this.media='all'">
    <noscript>
        <link rel="stylesheet" href="{prefix}css/premium.css">
        <link rel="stylesheet" href="{prefix}css/blog.css">
        <link rel="stylesheet" href="{prefix}css/responsive.css">
    </noscript>'''

    html_content = re.sub(css_pattern, css_replacement, html_content)

    # 3. Add defer to template-loader.js (preserve full path)
    html_content = re.sub(
        r'<script src="((?:\.\./)+)js/template-loader\.js"></script>',
        r'<script defer src="\1js/template-loader.js"></script>',
        html_content
    )

    return html_content


def process_blog_posts():
    """Process all blog posts in the posts directory."""
    posts_dir = Path('/home/rajesh/health.gheware.com/posts')

    updated_count = 0
    skipped_count = 0

    for html_file in posts_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Check if already updated
            if 'media="print" onload="this.media=' in original_content:
                print(f"SKIP (already updated): {html_file.name}")
                skipped_count += 1
                continue

            updated_content = fix_render_blocking(original_content)

            if updated_content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"UPDATED: {html_file.name}")
                updated_count += 1
            else:
                print(f"NO CHANGE: {html_file.name}")

        except Exception as e:
            print(f"ERROR: {html_file.name} - {e}")

    print(f"\n=== Summary ===")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")


if __name__ == '__main__':
    process_blog_posts()
