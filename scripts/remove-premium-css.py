#!/usr/bin/env python3
"""
Remove premium.css from blog posts to reduce unused CSS.

The critical.css now contains all variables needed by blog.css.
premium.css (32KB) is mostly unused on blog pages.

Changes:
1. Remove premium.css from async CSS loading
2. Remove premium.css from noscript fallback
"""

import re
from pathlib import Path


def remove_premium_css(html_content):
    """Remove premium.css references from HTML content."""

    # Check if this file has premium.css
    if 'premium.css' not in html_content:
        return html_content, False

    # Remove async-loaded premium.css line
    html_content = re.sub(
        r'\s*<link rel="stylesheet" href="[^"]*css/premium\.css" media="print" onload="this\.media=\'all\'">\n',
        '\n',
        html_content
    )

    # Remove noscript premium.css line
    html_content = re.sub(
        r'\s*<link rel="stylesheet" href="[^"]*css/premium\.css">\n',
        '\n',
        html_content
    )

    return html_content, True


def process_blog_posts():
    """Process all blog posts in the posts directory."""
    posts_dir = Path('/home/rajesh/health.gheware.com/posts')

    updated_count = 0
    skipped_count = 0

    for html_file in posts_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            updated_content, was_modified = remove_premium_css(original_content)

            if not was_modified:
                print(f"SKIP (no premium.css): {html_file.name}")
                skipped_count += 1
                continue

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
    print(f"\nPremium.css (~32KB) removed from {updated_count} blog posts")
    print(f"Estimated savings: ~32KB per page load")


if __name__ == '__main__':
    process_blog_posts()
