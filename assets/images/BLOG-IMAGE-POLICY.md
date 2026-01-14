# Blog Image Policy - Trade Gheware

**Date**: October 25, 2025  
**Policy**: Minimalist approach - Hero images only

---

## 📋 Current Policy

### ✅ What We Include
- **Hero images only**: One high-quality hero image per blog post
- **Purpose**: Social sharing (OG/Twitter cards), visual appeal, SEO
- **Location**: Background of blog post hero section

### ❌ What We Exclude
- **Step-by-step screenshots**: Too much maintenance, privacy concerns
- **Related post images**: Unnecessary page weight
- **Customer data**: No screenshots with real user information

---

## 🎯 Rationale

### Why Hero-Only Approach?

**Advantages:**
1. **Privacy Protection**: Less risk of exposing customer data
2. **Maintenance**: Only 1 image per post to update
3. **Performance**: Minimal page weight (263KB vs 2.4MB)
4. **Context Issues**: Avoids force-fitting screenshots to content
5. **Future-Proof**: UI changes don't break blog illustrations

**Trade-offs:**
- Less visual guidance for tutorials
- Users rely on text descriptions
- Lower engagement (possibly)

**Decision**: Privacy and maintenance > visual richness

---

## 📸 Hero Image Requirements

### Must Have
✅ High-resolution (minimum 1200x630 for social sharing)  
✅ Shows product/feature in context  
✅ No personal information (morphed if needed)  
✅ Optimized (under 300KB ideally)  
✅ Relevant to blog topic  

### File Naming
- Format: `{blog-slug}-hero.jpg`
- Example: `import-zerodha-portfolio-60-seconds-hero.jpg`

### Metadata
- **OG Image**: Used in social shares (Facebook, LinkedIn)
- **Twitter Card**: Used in tweets
- **Schema.org**: Included in BlogPosting/HowTo structured data
- **Hero Background**: Displayed in blog post header

---

## 🔄 Migration Complete

### Removed from Blog Post: `import-zerodha-portfolio-60-seconds.html`

**Before:**
- Hero image (540KB) - morphed
- Step 1 screenshot (540KB) - morphed
- Step 2 screenshot (377KB)
- Step 3 screenshot (332KB)
- Step 4 screenshot (242KB)
- Step 5 screenshot (266KB)
- Related post 1 (377KB)
- Related post 2 (266KB)
- Related post 3 (242KB)
- **Total**: 9 images, ~3.2MB

**After:**
- Hero image (263KB) - morphed, optimized
- **Total**: 1 image, 263KB

**Savings**: 2.9MB per page load (91.8% reduction)

---

## 📝 Best Practices

### For Hero Images

1. **Source**: Use homepage, dashboard, or feature overview screenshots
2. **Morphing**: Always anonymize customer data
   ```bash
   convert screenshot.jpg \
     \( +clone -region 200x20+700+135 -blur 0x8 \) -composite \
     -font "Liberation-Sans" -pointsize 13 -fill "#6b7280" \
     -annotate +710+146 "user@example.com" \
     hero-morphed.jpg
   ```
3. **Optimization**: Compress to 250-300KB
   ```bash
   convert hero.jpg -quality 85 -resize 1200x630^ -gravity center -extent 1200x630 hero-optimized.jpg
   ```

### For Tutorial Content (Text-Based)

Instead of screenshots, use:
- **Clear text descriptions**: "Click Holdings in left sidebar"
- **Code blocks**: For technical steps
- **Lists**: Numbered steps with bold UI elements
- **Callouts**: Tip boxes, warning boxes for emphasis

---

## 🎨 Current Hero Image Inventory

| Blog Post | Hero Image | Size | Status |
|-----------|-----------|------|--------|
| `import-zerodha-portfolio-60-seconds.html` | `import-zerodha-portfolio-60-seconds-hero.jpg` | 263KB | ✅ Morphed, Optimized |

---

## 🔒 Privacy Checklist for Hero Images

Before publishing any hero image:

- [ ] No real customer names visible
- [ ] No real email addresses visible (use user@example.com)
- [ ] No phone numbers visible
- [ ] No PII (Personally Identifiable Information)
- [ ] Portfolio values are anonymized or generic
- [ ] Stock holdings are public companies (not private positions)

---

## 📊 Performance Impact

### Page Load Analysis

**Before (9 images):**
- Total image weight: 3.2MB
- Images above fold: 2 (hero + step 1) = 1.08MB
- Lazy-loaded: 7 images = 2.12MB
- **LCP (Largest Contentful Paint)**: ~2.5s on 3G

**After (1 image):**
- Total image weight: 263KB
- Images above fold: 1 (hero only) = 263KB
- Lazy-loaded: 0 images
- **LCP (Largest Contentful Paint)**: ~0.8s on 3G

**Improvement**: 68% faster LCP, 91.8% less bandwidth

---

## 🚀 Future Considerations

### When to Add More Images

Only add screenshots if:
1. **Critical to understanding**: Text alone insufficient
2. **Privacy safe**: No customer data or morphed
3. **Context accurate**: Screenshot exactly matches content
4. **Optimized**: Under 200KB per image
5. **Maintained**: Team commits to updating with UI changes

### Alternatives to Screenshots

- **Video embeds**: YouTube tutorials (lazy-loaded iframes)
- **Diagrams**: Flowcharts, architecture diagrams (SVG)
- **Illustrations**: Custom graphics without personal data
- **GIFs**: Short interactions (optimized, under 500KB)

---

## 📞 Questions?

For questions about blog image policy:
- **Reference**: This document (BLOG-IMAGE-POLICY.md)
- **Updates**: Policy reviewed quarterly
- **Exceptions**: Discuss with team lead

---

**Last Updated**: October 25, 2025, 7:05 PM IST  
**Policy Owner**: Marketing Team  
**Status**: ✅ Active - Hero-only approach enforced
