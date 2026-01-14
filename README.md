# Health Gheware Blog

AI-powered diabetes management blog hosted on GitHub Pages.

## Live Site

- **Production URL:** https://health.gheware.com/blog
- **GitHub Pages:** https://brainupgrade-in.github.io/health.gheware.com-blogs

## Overview

This repository contains the static blog content for Health Gheware, featuring 79 health-focused articles covering:

- Diabetes management and education
- Time in Range optimization
- Glucose tracking and CGM data analysis
- Sleep-health correlations
- Nutrition and lifestyle tips
- Medication guides
- Research updates

## Structure

```
/
├── index.html              # Blog homepage with search and pagination
├── posts.json              # Blog metadata (76 posts)
├── feed.xml                # RSS feed
├── favicon.svg             # Site favicon
├── .nojekyll               # Disable Jekyll processing
├── css/
│   ├── premium.css         # Base design system
│   ├── blog.css            # Blog-specific styles
│   ├── blog-spacing.css    # Spacing utilities
│   └── animations.css      # Animation definitions
├── js/
│   ├── template-loader.js  # Dynamic template loading
│   └── analytics-loader.js # GA4 integration
├── templates/
│   ├── header.html         # Site header
│   ├── footer.html         # Site footer
│   └── author-bio.html     # Author section
├── images/
│   └── rajesh-gheware.jpg  # Author avatar
├── assets/
│   └── images/             # 91 hero images (1200x630px)
└── posts/
    ├── 2025/
    │   ├── 11/             # 36 health posts
    │   └── 12/             # 40 health posts
    └── 2026/
        └── 01/             # 3 health posts
```

## Deployment

This site is deployed via GitHub Pages and served through nginx reverse proxy at https://health.gheware.com/blog.

### GitHub Pages Setup

1. Repository Settings → Pages
2. Source: Deploy from branch `main`
3. Folder: `/ (root)`

### Nginx Configuration (health.gheware.com)

```nginx
location /blog {
    proxy_pass https://brainupgrade-in.github.io/health.gheware.com-blogs;
    proxy_set_header Host brainupgrade-in.github.io;
    proxy_ssl_server_name on;
    proxy_set_header X-Real-IP $remote_addr;
    sub_filter 'brainupgrade-in.github.io/health.gheware.com-blogs' 'health.gheware.com/blog';
    sub_filter_once off;
}
```

## Local Development

```bash
# Start local server
python3 -m http.server 8889

# Open in browser
open http://localhost:8889
```

## Content Statistics

- **Total Posts:** 79
- **Hero Images:** 91 (1200x630px)
- **Categories:** 14 health-related categories
- **Posts per Page:** 12

## Features

- Full-text search with debouncing
- Category filtering
- Dual pagination (top and bottom)
- Responsive design (mobile-first)
- RSS feed
- GA4 analytics integration
- Newsletter signup

## Related Repositories

- **Health Gheware App:** https://github.com/brainupgrade-in/health (main application)
- **Main Marketing Site:** https://github.com/brainupgrade-in/www-gheware

## License

Copyright 2025 Gheware Technologies. All rights reserved.
