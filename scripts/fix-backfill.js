#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const POSTS_DIR = '/home/openclaw/.openclaw/workspace/health.gheware.com-blogs/posts/2026/05';
const REF = fs.readFileSync('/tmp/ref-template.html', 'utf8').split('\n');

// Reference head boilerplate (always-present, never replaced):
// Line 1-6: DOCTYPE, html, head, charset, viewport
// Line 32-44: favicon, CSS preload, noscript, </head>
// Lines 7-31: title, meta desc, og, twitter, schema — REPLACE per post

const refTitle = REF[6].trim();  // line 7 (0-indexed 6)
const refMetaDesc = REF[7].trim(); // line 8
const refKeywords = REF[8].trim(); // line 9
const refAuthor = REF[9].trim(); // line 10
const refRobots = REF[10].trim(); // line 11
const refCanonical = REF[11].trim(); // line 12
const refOGStart = 12; // line 13
const refTwitterStart = 25; // line 26
const refFaviconStart = 31; // line 32
const refHeadEnd = 44; // line 45 (</head>)

const SKIP = 'beato-cgm-3999-review-india-2026.html';

for (const fname of fs.readdirSync(POSTS_DIR).filter(f => f.endsWith('.html')).sort()) {
  if (fname === SKIP) { console.log(`SKIP: ${fname}`); continue; }
  
  const fpath = path.join(POSTS_DIR, fname);
  const html = fs.readFileSync(fpath, 'utf8');
  
  // Extract title from h1 in article body
  const h1Match = html.match(/<article[^>]*>([\s\S]*?)<\/article>/);
  if (!h1Match) continue;
  
  const articleContent = h1Match[1];
  
  // Extract h1 title
  const titleMatch = articleContent.match(/<h1[^>]*>([\s\S]*?)<\/h1>/);
  let title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, '').trim() : fname.replace('.html', '');
  
  // Extract lead paragraph for meta description
  const leadMatch = articleContent.match(/<p[^>]*class="lead"[^>]*>([\s\S]*?)<\/p>/);
  let excerpt = leadMatch ? leadMatch[1].replace(/<[^>]+>/g, '').trim() : title;
  
  // Truncate excerpt for meta desc (120-170 chars target)
  if (excerpt.length > 170) excerpt = excerpt.substring(0, 167) + '...';
  
  // Truncate title to 65 chars max
  if (title.length > 65) {
    const truncated = title.substring(0, 65);
    const lastBreak = Math.max(
      truncated.lastIndexOf(':'), truncated.lastIndexOf(','),
      truncated.lastIndexOf('—'), truncated.lastIndexOf(' ')
    );
    if (lastBreak > 35) {
      title = truncated.substring(0, lastBreak).trim() + '…';
    } else {
      title = truncated.trim() + '…';
    }
  }
  
  const slug = fname.replace('.html', '');
  const postUrl = `https://health.gheware.com/blog/posts/2026/05/${fname}`;
  
  // Word count (article body)
  const bodyText = articleContent.replace(/<[^>]+>/g, ' ').replace(/&[^;]+;/g, ' ').replace(/\s+/g, ' ').trim();
  const wordCount = bodyText.split(/\s+/).length;
  
  // Build new head
  let head = '';
  head += REF[0] + '\n';  // DOCTYPE
  head += REF[1] + '\n';  // html lang
  head += REF[2] + '\n';  // <head>
  head += REF[3] + '\n';  // charset
  head += REF[4] + '\n';  // viewport
  head += `<title>${title}</title>\n`;
  head += `<meta content="${excerpt}" name="description"/>\n`;
  head += `<meta content="${slug.replace(/-/g, ' ')}, diabetes india, ${slug}" name="keywords"/>\n`;
  head += `<meta content="Health Gheware" name="author"/>\n`;
  head += `<meta content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" name="robots"/>\n`;
  head += '<!-- Open Graph / Facebook -->\n';
  head += '<meta content="article" property="og:type"/>\n';
  head += `<meta content="${postUrl}" property="og:url"/>\n`;
  head += `<meta content="${title}" property="og:title"/>\n`;
  head += `<meta content="${excerpt}" property="og:description"/>\n`;
  head += `<meta content="https://health.gheware.com/blog/assets/images/${slug}-hero.jpg" property="og:image"/>\n`;
  head += `<meta content="1200" property="og:image:width"/>\n`;
  head += `<meta content="630" property="og:image:height"/>\n`;
  head += '<meta content="Health Gheware" property="og:site_name"/>\n';
  head += '<!-- Twitter -->\n';
  head += '<meta content="summary_large_image" name="twitter:card"/>\n';
  head += `<meta content="${title}" name="twitter:title"/>\n`;
  head += `<meta content="${excerpt}" name="twitter:description"/>\n`;
  head += `<meta content="https://health.gheware.com/blog/assets/images/${slug}-hero.jpg" name="twitter:image"/>\n`;
  head += '<!-- Favicon -->\n';
  // Favicon and CSS from reference
  for (let i = refFaviconStart; i <= 43; i++) {
    head += REF[i] + '\n';
  }
  
  // Find </head> in original and replace everything before it with new head
  const lines = html.split('\n');
  let headEndIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('</head>')) {
      headEndIdx = i;
      break;
    }
  }
  
  if (headEndIdx < 0) {
    console.log(`SKIP (no </head>): ${fname}`);
    continue;
  }
  
  const rest = lines.slice(headEndIdx + 1).join('\n');
  const newHtml = head + '</head>\n' + rest;
  
  fs.writeFileSync(fpath, newHtml);
  console.log(`${fname}: title=${title.length}w, meta=${excerpt.length}w, words=${wordCount} ✓${(title.length<=65 && excerpt.length>=120 && excerpt.length<=170) ? '' : '!!'}`);
}
