#!/usr/bin/env python3
"""
Replace inline author bio sections with template placeholder.
This script finds various author bio patterns and replaces them with:
<div id="author-bio-placeholder"></div>

Usage: python3 replace_author_bio_with_template.py [--dry-run]
"""

import re
import sys
from pathlib import Path

def replace_author_bio(content):
    """Replace inline author bio with template placeholder."""

    # Check if already using template placeholder
    if 'id="author-bio-placeholder"' in content:
        return content, False

    # Check if there's an author bio to replace
    if 'author-links' not in content:
        return content, False

    # Pattern: div.author-bio with itemscope containing author-links
    # Match from opening <div class="author-bio" to the closing </div> that ends this section
    # The structure is: div.author-bio > img + div.author-info > div.author-name-row + p
    pattern = r'<div class="author-bio"[^>]*itemscope[^>]*>[\s\S]*?<div class="author-links"[^>]*>[\s\S]*?</div>\s*</div>\s*<p[^>]*itemprop="description"[^>]*>[\s\S]*?</p>\s*</div>\s*</div>'

    placeholder = '<!-- Author Bio -->\n            <div id="author-bio-placeholder"></div>'

    new_content, count = re.subn(pattern, placeholder, content, flags=re.DOTALL)
    if count > 0:
        print(f"  Replaced {count} author bio(s)")
        return new_content, True

    # Fallback pattern - simpler match for author-bio div containing author-links
    pattern2 = r'<div class="author-bio"[^>]*>[\s\S]*?</div>\s*</div>\s*</div>\s*(?=\s*<!-- Content Review|\s*<p class="content-review)'
    new_content, count = re.subn(pattern2, placeholder + '\n\n            ', content, flags=re.DOTALL)
    if count > 0:
        print(f"  [Fallback] Replaced {count} author bio(s)")
        return new_content, True

    return content, False

def process_file(filepath, dry_run=False):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified_content, changed = replace_author_bio(content)

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
    already_template = 0
    no_author = 0

    for filepath in sorted(html_files):
        relative_path = filepath.relative_to(posts_dir)

        # Check current state
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'id="author-bio-placeholder"' in content:
            already_template += 1
            continue

        if 'author-links' not in content:
            no_author += 1
            continue

        print(f"\n{'[WOULD MODIFY] ' if dry_run else '[MODIFYING] '}{relative_path}")
        modified = process_file(filepath, dry_run)
        if modified:
            modified_count += 1
        else:
            print("  [SKIPPED] Pattern not matched")

    print("\n" + "-" * 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Total files scanned: {len(html_files)}")
    print(f"  Files modified: {modified_count}")
    print(f"  Already using template: {already_template}")
    print(f"  No author bio found: {no_author}")

    if dry_run:
        print("\nRun without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
