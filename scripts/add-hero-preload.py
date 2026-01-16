#!/usr/bin/env python3
"""
Add hero image preload to blog posts for faster LCP.

Changes:
1. Extract hero image URL from blog-post-hero section
2. Add preload link with fetchpriority="high"
"""

import re
from pathlib import Path


def add_hero_preload(html_content):
    """Add hero image preload to HTML content."""

    # First check if this is a blog-post-hero with background image
    if 'class="blog-post-hero"' not in html_content:
        return html_content, None

    # Extract hero image URL - try with single quotes first
    hero_pattern = r"url\('([^']+\.jpg)'\)"
    hero_match = re.search(hero_pattern, html_content)

    if not hero_match:
        # Try with double quotes
        hero_pattern = r'url\("([^"]+\.jpg)"\)'
        hero_match = re.search(hero_pattern, html_content)

    if not hero_match:
        # Try without quotes
        hero_pattern = r'url\(([^)\s]+\.jpg)\)'
        hero_match = re.search(hero_pattern, html_content)

    if not hero_match:
        return html_content, None

    hero_image_url = hero_match.group(1)

    # Check if hero preload already exists (not just any preload)
    if 'Hero Image Preload for LCP' in html_content:
        return html_content, None

    # Create preload link
    preload_link = f'<link rel="preload" as="image" href="{hero_image_url}" fetchpriority="high">'

    # Insert preload after critical CSS preload (or before CSS section)
    # Look for the critical CSS preload line
    insert_pattern = r'(<!-- Critical CSS Preload -->[\s\S]*?<link rel="preload" href="[^"]*css/critical\.css"[^>]*>)'

    if re.search(insert_pattern, html_content):
        # Insert hero preload after critical CSS preload
        html_content = re.sub(
            insert_pattern,
            r'\1\n    <!-- Hero Image Preload for LCP -->\n    ' + preload_link,
            html_content
        )
    else:
        # Fallback: insert before </head>
        html_content = html_content.replace(
            '</head>',
            f'    <!-- Hero Image Preload for LCP -->\n    {preload_link}\n</head>'
        )

    return html_content, hero_image_url


def process_blog_posts():
    """Process all blog posts in the posts directory."""
    posts_dir = Path('/home/rajesh/health.gheware.com/posts')

    updated_count = 0
    skipped_count = 0
    no_hero_count = 0

    for html_file in posts_dir.rglob('*.html'):
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Check if already has hero preload
            if 'Hero Image Preload for LCP' in original_content:
                print(f"SKIP (already has preload): {html_file.name}")
                skipped_count += 1
                continue

            updated_content, hero_url = add_hero_preload(original_content)

            if hero_url is None:
                print(f"NO HERO: {html_file.name}")
                no_hero_count += 1
                continue

            if updated_content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"UPDATED: {html_file.name} -> {hero_url}")
                updated_count += 1

        except Exception as e:
            print(f"ERROR: {html_file.name} - {e}")

    print(f"\n=== Summary ===")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count}")
    print(f"No hero image: {no_hero_count}")


if __name__ == '__main__':
    process_blog_posts()
