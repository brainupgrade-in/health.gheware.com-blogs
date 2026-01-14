#!/usr/bin/env python3
"""
Remove inline newsletter sections from all blog posts.
Keeps the footer newsletter (in templates/footer.html) as the single source.

Usage: python3 remove_inline_newsletter.py [--dry-run]
"""

import re
import sys
from pathlib import Path

def remove_newsletter_section(content):
    """Remove the inline newsletter HTML section from blog post content."""

    total_changes = 0

    # Pattern 1: Newsletter with class="container" wrapper
    newsletter_html_pattern1 = r'\s*<!-- Newsletter Section -->\s*<div class="container"[^>]*style="[^"]*background:\s*linear-gradient[^"]*"[^>]*>.*?</div>\s*'
    content, count1 = re.subn(newsletter_html_pattern1, '\n\n', content, flags=re.DOTALL)
    total_changes += count1

    # Pattern 2: Newsletter with direct div style (no class="container")
    newsletter_html_pattern2 = r'\s*<!-- Newsletter Section -->\s*<div style="background:\s*linear-gradient[^"]*"[^>]*>.*?</div>\s*'
    content, count2 = re.subn(newsletter_html_pattern2, '\n\n', content, flags=re.DOTALL)
    total_changes += count2

    # Pattern 2b: Newsletter with section tag instead of div
    newsletter_html_pattern2b = r'\s*<!-- Newsletter Section -->\s*<section[^>]*style="[^"]*background:\s*linear-gradient[^"]*"[^>]*>.*?</section>\s*'
    content, count2b = re.subn(newsletter_html_pattern2b, '\n\n', content, flags=re.DOTALL)
    total_changes += count2b

    # Pattern 3: Newsletter JavaScript handler (newsletterForm variant) with if check
    newsletter_js_pattern1 = r'\s*// Newsletter form submission\s*if \(document\.getElementById\([\'"]newsletterForm[\'"]\)\) \{[^}]*document\.getElementById\([\'"]newsletterForm[\'"]\)\.addEventListener\([\'"]submit[\'"],\s*async\s*\(e\)\s*=>\s*\{.*?\}\);\s*\}'
    content, count3 = re.subn(newsletter_js_pattern1, '', content, flags=re.DOTALL)
    total_changes += count3

    # Pattern 4: Newsletter JavaScript handler (newsletter-form variant with script tags)
    newsletter_js_pattern2 = r'\s*<script>\s*document\.getElementById\([\'"]newsletter-form[\'"]\)\.addEventListener\([\'"]submit[\'"],\s*async\s*function\(e\)\s*\{.*?\}\);\s*</script>'
    content, count4 = re.subn(newsletter_js_pattern2, '', content, flags=re.DOTALL)
    total_changes += count4

    # Pattern 5: Newsletter JavaScript handler (const assignment variant)
    newsletter_js_pattern3 = r'\s*// Newsletter form submission\s*const newsletterForm = document\.getElementById\([\'"]newsletterForm[\'"]\);\s*if \(newsletterForm\) \{\s*newsletterForm\.addEventListener\([\'"]submit[\'"],\s*async\s*\(e\)\s*=>\s*\{.*?\}\);\s*\}'
    content, count5 = re.subn(newsletter_js_pattern3, '', content, flags=re.DOTALL)
    total_changes += count5

    # Pattern 6: Simpler newsletter form handler (newsletter-form id)
    newsletter_js_pattern4 = r"\s*document\.getElementById\('newsletter-form'\)\.addEventListener\('submit',\s*async\s*function\(e\)\s*\{.*?\}\);"
    content, count6 = re.subn(newsletter_js_pattern4, '', content, flags=re.DOTALL)
    total_changes += count6

    # Pattern 7: Newsletter handler inside templatesLoaded with const assignment (ending with closing bracket)
    newsletter_js_pattern5 = r"\s*const newsletterForm = document\.getElementById\('newsletterForm'\);\s*if \(newsletterForm\) \{\s*newsletterForm\.addEventListener\('submit', async \(e\) => \{.*?\}\);\s*\}\s*"
    content, count7 = re.subn(newsletter_js_pattern5, '\n\n            ', content, flags=re.DOTALL)
    total_changes += count7

    # Pattern 8: <!-- Newsletter CTA --> with div and inline script
    newsletter_cta_pattern = r'\s*<!-- Newsletter CTA -->\s*<div[^>]*style="[^"]*background:\s*linear-gradient[^"]*"[^>]*>.*?</div>\s*<script>.*?newsletter.*?</script>\s*'
    content, count8 = re.subn(newsletter_cta_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count8

    # Pattern 8b: <!-- Newsletter CTA --> div only (no inline script)
    newsletter_cta_pattern2 = r'\s*<!-- Newsletter CTA -->\s*<div[^>]*style="[^"]*background:\s*linear-gradient[^"]*"[^>]*>.*?</div>\s*'
    content, count8b = re.subn(newsletter_cta_pattern2, '\n\n', content, flags=re.DOTALL)
    total_changes += count8b

    # Pattern 8c: Remove orphaned <!-- Newsletter Form Handler --> comment
    newsletter_handler_comment = r'\s*<!-- Newsletter Form Handler -->\s*'
    content, count8c = re.subn(newsletter_handler_comment, '\n', content, flags=re.DOTALL)
    total_changes += count8c

    # Pattern 9: <!-- Newsletter Signup --> section with class="newsletter-signup"
    newsletter_signup_pattern = r'\s*<!-- Newsletter Signup -->\s*<section class="newsletter-signup">.*?</section>\s*'
    content, count9 = re.subn(newsletter_signup_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count9

    # Pattern 9b: <!-- Newsletter Signup --> div with class="newsletter-signup"
    newsletter_signup_div_pattern = r'\s*<!-- Newsletter Signup -->\s*<div class="newsletter-signup"[^>]*>.*?</div>\s*'
    content, count9b = re.subn(newsletter_signup_div_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count9b

    # Pattern 9c: <!-- Newsletter Signup --> div without class (just style)
    newsletter_signup_style_pattern = r'\s*<!-- Newsletter Signup -->\s*<div style="[^"]*background:\s*linear-gradient[^"]*"[^>]*>.*?</div>\s*'
    content, count9c = re.subn(newsletter_signup_style_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count9c

    # Pattern 9d: <!-- Newsletter Signup --> section with class="newsletter-section"
    newsletter_section_pattern = r'\s*<!-- Newsletter Signup -->\s*<section class="newsletter-section"[^>]*>.*?</section>\s*'
    content, count9d = re.subn(newsletter_section_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count9d

    # Pattern 10: <!-- Newsletter Signup (Health Gheware) --> with class="newsletter-health-signup"
    newsletter_health_pattern = r'\s*<!-- Newsletter Signup \(Health Gheware\) -->\s*<div class="newsletter-health-signup"[^>]*>.*?</div>\s*'
    content, count10 = re.subn(newsletter_health_pattern, '\n\n', content, flags=re.DOTALL)
    total_changes += count10

    # Pattern 11: Orphaned newsletter comments (cleanup)
    orphan_comment_pattern = r'\s*<!-- Newsletter[^>]*-->\s*(?=\n)'
    content, count11 = re.subn(orphan_comment_pattern, '\n', content)
    total_changes += count11

    return content, total_changes

def process_file(filepath, dry_run=False):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    modified_content, changes = remove_newsletter_section(original_content)

    if changes > 0:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        return True, changes
    return False, 0

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
    total_changes = 0

    for filepath in sorted(html_files):
        modified, changes = process_file(filepath, dry_run)
        if modified:
            modified_count += 1
            total_changes += changes
            relative_path = filepath.relative_to(posts_dir)
            print(f"{'[WOULD MODIFY] ' if dry_run else '[MODIFIED] '}{relative_path} ({changes} change(s))")

    print("-" * 60)
    print(f"{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Total files scanned: {len(html_files)}")
    print(f"  Files {'to be ' if dry_run else ''}modified: {modified_count}")
    print(f"  Total changes: {total_changes}")

    if dry_run:
        print("\nRun without --dry-run to apply changes.")

if __name__ == '__main__':
    main()
