#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const POSTS_DIR = '/home/openclaw/.openclaw/workspace/health.gheware.com-blogs/posts/2026/05';
const SKIP = 'beato-cgm-3999-review-india-2026.html';

for (const fname of fs.readdirSync(POSTS_DIR).filter(f => f.endsWith('.html')).sort()) {
  if (fname === SKIP) { console.log(`SKIP: ${fname}`); continue; }
  
  const fpath = path.join(POSTS_DIR, fname);
  const html = fs.readFileSync(fpath, 'utf8');
  
  // Extract title from h1 in article
  const articleMatch = html.match(/<article[\s\S]*?>([\s\S]*?)<\/article>/);
  if (!articleMatch) { console.log(`SKIP (no article): ${fname}`); continue; }
  
  const article = articleMatch[1];
  
  // h1 title
  const h1Match = article.match(/<h1[\s\S]*?>([\s\S]*?)<\/h1>/);
  let title = h1Match ? h1Match[1].replace(/<[^>]+>/g, '').trim() : fname.replace('.html', '');
  
  // Lead paragraph for meta
  const leadMatch = article.match(/<p[\s\S]*?class="lead"[\s\S]*?>([\s\S]*?)<\/p>/);
  let meta = leadMatch ? leadMatch[1].replace(/<[^>]+>/g, '').trim() : title;
  if (meta.length > 170) meta = meta.substring(0, 167) + '...';
  
  // Truncate title to 65 chars
  if (title.length > 65) {
    const t = title.substring(0, 65);
    const breakAt = Math.max(t.lastIndexOf(':'), t.lastIndexOf(','), t.lastIndexOf(' '), t.lastIndexOf('—'));
    title = breakAt > 35 ? t.substring(0, breakAt).trim() + '…' : t.trim() + '…';
  }
  
  // Word count
  const words = article.replace(/<[^>]+>/g, ' ').replace(/&[^;]+;/g, ' ').replace(/\s+/g, ' ').trim().split(/\s+/).length;
  
  const slug = fname.replace('.html', '');
  const url = `https://health.gheware.com/blog/posts/2026/05/${fname}`;
  
  // Find head start and end
  const lines = html.split('\n');
  let htmlStart = '';
  let headEnd = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('<!DOCTYPE')) htmlStart = lines[i] + '\n';
    if (lines[i].includes('</head>')) { headEnd = i; break; }
  }
  
  // Build new head section
  const headLines = [];
  headLines.push('<html lang="en-IN">');
  headLines.push('<head>');
  headLines.push('<meta charset="utf-8"/>');
  headLines.push('<meta content="width=device-width, initial-scale=1.0" name="viewport"/>');
  headLines.push(`<title>${title}</title>`);
  headLines.push(`<meta content="${meta}" name="description"/>`);
  headLines.push(`<meta content="Health Gheware" name="author"/>`);
  headLines.push('<meta content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" name="robots"/>');
  
  // OG tags
  headLines.push('<!-- Open Graph / Facebook -->');
  headLines.push('<meta content="article" property="og:type"/>');
  headLines.push(`<meta content="${url}" property="og:url"/>`);
  headLines.push(`<meta content="${title}" property="og:title"/>`);
  headLines.push(`<meta content="${meta}" property="og:description"/>`);
  headLines.push(`<meta content="https://health.gheware.com/blog/assets/images/${slug}-hero.jpg" property="og:image"/>`);
  headLines.push('<meta content="1200" property="og:image:width"/>');
  headLines.push('<meta content="630" property="og:image:height"/>');
  headLines.push('<meta content="Health Gheware" property="og:site_name"/>');
  
  // Twitter
  headLines.push('<!-- Twitter -->');
  headLines.push('<meta content="summary_large_image" name="twitter:card"/>');
  headLines.push(`<meta content="${title}" name="twitter:title"/>`);
  headLines.push(`<meta content="${meta}" name="twitter:description"/>`);
  headLines.push(`<meta content="https://health.gheware.com/blog/assets/images/${slug}-hero.jpg" name="twitter:image"/>`);
  
  // Favicon and CSS (from reference template)
  headLines.push('<!-- Favicon -->');
  headLines.push('<link href="/blog/favicon.svg" rel="icon" type="image/x-icon"/>');
  headLines.push('<!-- Critical CSS Preload -->');
  headLines.push('<link as="style" href="../../../css/critical.css" rel="preload"/>');
  headLines.push('<!-- Hero Image Preload for LCP -->');
  headLines.push('<link as="image" fetchpriority="high" href="../../../assets/images/share-health-data-hero.jpg" rel="preload"/>');
  headLines.push('<!-- CSS (async loaded for non-blocking render) -->');
  headLines.push('<link href="../../../css/critical.css" rel="stylesheet"/>');
  headLines.push('<link href="../../../css/blog.css" media="print" onload="this.media=\'all\'" rel="stylesheet"/>');
  headLines.push('<link href="../../../css/responsive.css" media="print" onload="this.media=\'all\'" rel="stylesheet"/>');
  headLines.push('<noscript>');
  headLines.push('<link href="../../../css/blog.css" rel="stylesheet"/>');
  headLines.push('<link href="../../../css/responsive.css" rel="stylesheet"/>');
  headLines.push('</noscript>');
  
  // Rebuild
  const headHtml = headLines.join('\n') + '\n</head>';
  const rest = lines.slice(headEnd + 1).join('\n');
  const newHtml = htmlStart + headHtml + '\n\n' + rest;
  
  fs.writeFileSync(fpath, newHtml);
  console.log(`${fname}: title="${title.substring(0,50)}..." (${title.length}w) meta=${meta.length}w words=${words} ${(title.length <= 65 && meta.length >= 120 && meta.length <= 170) ? '✓' : '!!'}`);
}
