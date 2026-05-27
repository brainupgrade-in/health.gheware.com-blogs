#!/usr/bin/env python3
"""Add internal /blog/posts/ links to posts that have 0."""
import re, os

os.chdir('/home/openclaw/.openclaw/workspace')
posts_dir = 'health.gheware.com-blogs/posts/2026/05'

# Cross-link map: which posts should link to which
link_map = {
    'beato-clinical-study-ada-2023-attd-results-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/04/cgm-pricing-wars-india-2026-beato-vs-ultrahuman-vs-abbott.html', 'CGM pricing wars analysis'),
        ('https://health.gheware.com/blog/posts/2026/04/diabetes-ai-chatbot-comparison-india-2026.html', 'AI diabetes chatbot comparison'),
    ],
    'cgm-gestational-diabetes-india-2026-guide.html': [
        ('https://health.gheware.com/blog/posts/2026/05/ultrahuman-ring-worth-it-diabetes-india-2026.html', 'Ultrahuman Ring PRO for diabetics'),
        ('https://health.gheware.com/blog/posts/2026/05/ultrahuman-jade-ai-biointelligence-review-india-2026.html', 'Ultrahuman Jade AI review'),
    ],
    'diabetes-oral-health-gum-disease-india-guide-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1 program'),
        ('https://health.gheware.com/blog/posts/2026/05/indian-kitchen-spices-lower-blood-sugar-icmr-research-2026.html', 'Indian spices for blood sugar'),
    ],
    'dtechcon-diabetes-tech-conference-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1 review'),
        ('https://health.gheware.com/blog/posts/2026/05/ragus-ai-vs-beato-ai-diabetes-chatbot-comparison-india-2026.html', 'AI chatbot comparison'),
    ],
    'indian-kitchen-spices-lower-blood-sugar-icmr-research-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1 weight loss'),
        ('https://health.gheware.com/blog/posts/2026/05/beato-cgm-3999-review-india-2026.html', 'BeatO CGM review'),
    ],
    'ragus-ai-vs-beato-ai-diabetes-chatbot-comparison-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1 program'),
        ('https://health.gheware.com/blog/posts/2026/05/beato-cgm-3999-review-india-2026.html', 'BeatO CGM'),
    ],
    'sugarfit-glp1-weight-loss-program-review-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-revenue-growth-ada-2025-research-india-2026.html', 'Sugar.fit revenue growth'),
        ('https://health.gheware.com/blog/posts/2026/05/beato-clinical-study-ada-2023-attd-results-india-2026.html', 'BeatO clinical study'),
    ],
    'sugarfit-revenue-growth-ada-2025-research-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1 review'),
        ('https://health.gheware.com/blog/posts/2026/05/ultrahuman-jade-ai-biointelligence-review-india-2026.html', 'Ultrahuman Jade AI'),
    ],
    'ultrahuman-jade-ai-biointelligence-review-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/ultrahuman-ring-worth-it-diabetes-india-2026.html', 'Ultrahuman Ring PRO'),
        ('https://health.gheware.com/blog/posts/2026/05/diabetes-oral-health-gum-disease-india-guide-2026.html', 'Diabetes and oral health'),
    ],
    'ultrahuman-ring-worth-it-diabetes-india-2026.html': [
        ('https://health.gheware.com/blog/posts/2026/05/cgm-gestational-diabetes-india-2026-guide.html', 'CGM for gestational diabetes'),
        ('https://health.gheware.com/blog/posts/2026/05/sugarfit-glp1-weight-loss-program-review-india-2026.html', 'Sugar.fit GLP-1'),
    ],
}

for fname, links in link_map.items():
    fpath = os.path.join(posts_dir, fname)
    with open(fpath) as f:
        html = f.read()

    # Convert existing internal links from relative to absolute paths
    html = re.sub(
        r'href="((?:\.\./)+\d{4}/\d{2}/[^"]+)"',
        lambda m: 'href="/blog' + m.group(1).replace('../', ''),
        html
    )
    html = re.sub(
        r'href="https://health\.gheware\.com/blog/posts/\d{4}/\d{2}/([^"]+)"',
        r'href="/blog/posts/\1"',
        html
    )

    # Check current count of /blog/posts/ links
    current_links = re.findall(r'href="/blog/posts/[^"]+"', html)
    print(f"  {fname}: {len(current_links)} internal links before")

    # Find the closing </article> tag and insert links before it
    # Add links as a new <p> paragraph before </article>
    if len(current_links) < 2:
        link_text_parts = []
        for url, anchor in links:
            # Convert absolute URL to /blog/posts/ path
            path_match = re.search(r'/blog/posts/\d{4}/\d{2}/([^"]+)', url)
            if path_match:
                link_text_parts.append(f'<a href="/blog/posts/{path_match.group(1)}">{anchor}</a>')
        
        if link_text_parts:
            link_paragraph = (
                f'<p><strong>Read more:</strong> '
                f'{", ".join(link_text_parts[:-1])}'
                f' and {link_text_parts[-1]}.'
                f'</p>\n'
            )
            # Insert before </article>
            html = html.replace('</article>', link_paragraph + '</article>')
            print(f"    Added: {len(link_text_parts)} links")

    with open(fpath, 'w') as f:
        f.write(html)

    # Verify
    final_links = re.findall(r'href="/blog/posts/[^"]+"', html)
    print(f"  {fname}: {len(final_links)} internal links after")

print("Done!")
