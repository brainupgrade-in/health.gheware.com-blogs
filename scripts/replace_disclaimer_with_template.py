#!/usr/bin/env python3
"""
Replace inline disclaimer boxes with template placeholder.
This script finds various disclaimer patterns and replaces them with:
<div id="disclaimer-placeholder"></div>

Usage: python3 replace_disclaimer_with_template.py [--dry-run]
"""

import re
import sys
from pathlib import Path

def replace_disclaimer(content):
    """Replace inline disclaimer with template placeholder."""

    # Check if already using template placeholder
    if 'id="disclaimer-placeholder"' in content:
        return content, False

    # Check if there's a disclaimer-box to replace
    if 'disclaimer-box' not in content and 'Medical Disclaimer' not in content:
        return content, False

    original_content = content

    # Pattern 1: <!-- Medical Disclaimer --> comment followed by div.disclaimer-box
    # This is the most common pattern
    pattern1 = r'<!-- Medical Disclaimer -->\s*<div class="disclaimer-box"[^>]*>.*?</div>\s*(?=\s*<!--|\s*<div id="footer|\s*</article|\s*<script)'

    # Pattern 2: div.disclaimer-box without comment (with inline styles)
    pattern2 = r'<div class="disclaimer-box"[^>]*>.*?</div>\s*(?=\s*<!--|\s*<div id="footer|\s*</article|\s*<script)'

    # Pattern 3: <!-- Medical Disclaimer --> with inline styled div (no class)
    pattern3 = r'<!-- Medical Disclaimer -->\s*<div style="[^"]*(?:background:\s*#fef2f2|border-left:\s*4px solid)[^"]*"[^>]*>.*?</div>\s*(?=\s*</div>|\s*<!--|\s*<script)'

    # Pattern 4: Standalone inline styled disclaimer div
    pattern4 = r'<div style="[^"]*margin-top:\s*3rem[^"]*background:\s*#fef2f2[^"]*"[^>]*>\s*<h4[^>]*>.*?Medical Disclaimer.*?</div>\s*(?=\s*</div>|\s*<script)'

    placeholder = '\n    <!-- Medical Disclaimer -->\n    <div id="disclaimer-placeholder"></div>\n'

    # Try each pattern
    for i, pattern in enumerate([pattern1, pattern2, pattern3, pattern4], 1):
        new_content, count = re.subn(pattern, placeholder, content, flags=re.DOTALL)
        if count > 0:
            print(f"  [Pattern {i}] Replaced {count} disclaimer(s)")
            content = new_content
            break

    # If none of the patterns matched, try a more aggressive approach
    if content == original_content and 'disclaimer-box' in content:
        # Find the disclaimer-box and replace it along with all its content
        # This handles nested paragraphs
        pattern_aggressive = r'<div class="disclaimer-box"[^>]*>[\s\S]*?</div>\s*(?=\s*<!--\s*Footer|\s*<div id="footer|\s*</article)'
        new_content, count = re.subn(pattern_aggressive, placeholder, content, flags=re.DOTALL)
        if count > 0:
            print(f"  [Aggressive pattern] Replaced {count} disclaimer(s)")
            content = new_content

    return content, content != original_content

def process_file(filepath, dry_run=False):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    modified_content, changed = replace_disclaimer(original_content)

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
    skipped_count = 0
    already_template = 0

    for filepath in sorted(html_files):
        relative_path = filepath.relative_to(posts_dir)

        # Check current state
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'id="disclaimer-placeholder"' in content:
            already_template += 1
            continue

        if 'disclaimer-box' not in content and 'Medical Disclaimer' not in content:
            skipped_count += 1
            continue

        print(f"\n{'[WOULD MODIFY] ' if dry_run else '[MODIFYING] '}{relative_path}")
        modified = process_file(filepath, dry_run)
        if modified:
            modified_count += 1

    print("\n" + "-" * 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Total files scanned: {len(html_files)}")
    print(f"  Files modified: {modified_count}")
    print(f"  Already using template: {already_template}")
    print(f"  No disclaimer found: {skipped_count}")

    if dry_run:
        print("\nRun without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
