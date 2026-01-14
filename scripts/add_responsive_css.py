#!/usr/bin/env python3
"""
Add responsive.css to all blog posts that don't already have it.
This ensures mobile-first responsive design across all pages.

Usage: python3 add_responsive_css.py [--dry-run]
"""

import re
import sys
from pathlib import Path

def add_responsive_css(content):
    """Add responsive.css link after blog.css if not already present."""

    # Check if responsive.css is already included
    if 'responsive.css' in content:
        return content, False

    # Pattern to find the blog.css link and add responsive.css after it
    # Handle different relative paths (../../, ../../../, etc.)
    pattern = r'(<link rel="stylesheet" href="([\.\/]+)css/blog\.css">)'

    def add_responsive(match):
        original = match.group(1)
        path_prefix = match.group(2)
        return f'{original}\n    <link rel="stylesheet" href="{path_prefix}css/responsive.css">'

    new_content, count = re.subn(pattern, add_responsive, content, count=1)

    return new_content, count > 0

def process_file(filepath, dry_run=False):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    modified_content, changed = add_responsive_css(original_content)

    if changed:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        return True
    return False

def main():
    dry_run = '--dry-run' in sys.argv

    posts_dir = Path('/home/rajesh/health.gheware.com/posts')

    if not posts_dir.exists():
        print(f"Error: Posts directory not found: {posts_dir}")
        sys.exit(1)

    html_files = list(posts_dir.rglob('*.html'))

    print(f"{'[DRY RUN] ' if dry_run else ''}Processing {len(html_files)} HTML files...")
    print("-" * 60)

    modified_count = 0

    for filepath in sorted(html_files):
        modified = process_file(filepath, dry_run)
        if modified:
            modified_count += 1
            relative_path = filepath.relative_to(posts_dir)
            print(f"{'[WOULD MODIFY] ' if dry_run else '[MODIFIED] '}{relative_path}")

    print("-" * 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Total files scanned: {len(html_files)}")
    print(f"  Files {'to be ' if dry_run else ''}modified: {modified_count}")
    print(f"  Files already have responsive.css: {len(html_files) - modified_count}")

    if dry_run:
        print("\nRun without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
