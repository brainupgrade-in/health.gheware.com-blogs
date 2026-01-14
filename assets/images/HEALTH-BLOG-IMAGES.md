# Health Gheware Blog - Hero Image Requirements

**Date:** November 6, 2025
**Purpose:** Design specifications for Health Gheware blog post hero images
**Status:** ✅ Launch Image Created

---

## 📸 Required Images

### 1. Launch Post Hero Image ✅ COMPLETED
**Filename:** `health-gheware-launch.jpg`
**Size:** 1200x630px (16:9 aspect ratio)
**File Size:** 54.7KB (optimized)
**Status:** ✅ CREATED - November 6, 2025

**Design Implementation:**
- **Theme:** AI + Health + Data Correlation
- **Color Palette:**
  - Background: Navy blue (#1e3a8a) to lighter blue (#3b82f6) gradient
  - Accents: Bright green (#10b981), Teal (#14b8a6), Light blue (#60a5fa)
  - Glucose indicators: Red (#ef4444)
- **Visual Elements Created:**
  - ✅ Data correlation networks with connected nodes (showing AI)
  - ✅ Heartbeat/ECG line graphs in green (health vitals)
  - ✅ Glucose drop indicators (red circles with highlights)
  - ✅ Semi-transparent grid overlay (100px spacing, white 30% opacity)
  - ✅ Decorative circles of various sizes with transparency
  - ✅ "gheware.com" branding in bottom right corner

**Technical Details:**
- Created with: Python/PIL (Pillow) - Script: `marketing/create-health-hero.py`
- Background: Gradient + grid overlay + data visualization elements
- Style consistency: Matches existing Trade Gheware blog hero images
- Accessibility: Includes proper `role="img"` and descriptive `aria-label`

**Usage in Blog Post:**
```html
<section class="blog-post-hero"
  style="background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)),
  url('../../../assets/images/health-gheware-launch.jpg') center/cover no-repeat;"
  role="img"
  aria-label="Health Gheware hero image showing AI-powered diabetes management with data correlations">
```

**Generator Script:** Reusable Python script at `marketing/create-health-hero.py` for creating similar images

**Tools to Use:**
- **Canva** - https://canva.com
  - Template: Social Media > Custom Size (1200x630px)
  - Search elements: "glucose monitor", "health tech", "AI healthcare", "diabetes"
- **Figma** - Professional design tool
- **Adobe Photoshop/Illustrator** - If available
- **AI Image Generators** (with caution for medical accuracy):
  - Midjourney: `/imagine prompt: modern diabetes glucose monitor with AI neural network overlay, medical blue gradient background, clean professional health tech aesthetic, 1200x630`
  - DALL-E 3: "Professional medical technology hero image showing glucose monitoring device with AI visualization, modern blue gradient, healthcare app aesthetic"

---

### 2. Template for Future Health Blog Images
**Filename Pattern:** `{post-slug}.jpg`
**Size:** 1200x630px
**Consistency:** Maintain brand identity across all health posts

**Brand Guidelines for Health Gheware Blog Images:**

1. **Color Consistency**
   - Always use medical blue (#2563eb) as primary
   - Accent with health green (#10b981) or wellness teal
   - Background gradients, never solid colors

2. **Visual Elements Library**
   - CGM sensors/devices
   - Heart rate monitors
   - Sleep tracking visuals
   - Activity/fitness icons
   - Food/nutrition symbols
   - AI/technology patterns
   - Data visualizations (charts, graphs)

3. **Typography on Images**
   - Font: Inter or similar sans-serif
   - Bold for headlines
   - Keep text minimal (5-7 words max)
   - High contrast (white text on dark areas)

4. **Icon Style**
   - Consistent emoji usage: 🤖 (AI), 🩺 (Diabetes), 😴 (Sleep), 🏃 (Activity), 🍽️ (Nutrition)
   - Or: Use line-art icons in brand colors
   - Avoid mixing emoji and custom icons

5. **Image Composition**
   - Rule of thirds
   - Important elements in center (for cropping safety)
   - Leave space for text overlays
   - Balance between tech and human elements

---

## 🎨 Quick Design Templates

### Canva Template Recommendations

**For Launch/Announcement Posts:**
1. Search "Technology Launch" templates
2. Customize with medical blue color scheme
3. Replace generic tech with health tech imagery
4. Add glucose monitoring visual elements

**For Educational Posts:**
1. Search "Educational Infographic" templates
2. Use clean, minimal design
3. Include data visualization elements
4. Add medical credibility markers

**For Tutorial Posts:**
1. Search "Step-by-Step Guide" templates
2. Show app interface screenshots
3. Clear, instructional visuals
4. Arrows and annotations

---

## 📋 Image Specifications

### Technical Requirements
- **Format:** JPG (preferred for photos), PNG (for transparency needs)
- **Resolution:** 1200x630px (Open Graph standard)
- **File Size:** < 500KB (optimized for web)
- **Color Profile:** sRGB (web standard)
- **Compression:** 80-85% quality (balance between quality and file size)

### SEO Image Optimization
- **Alt Text:** Always include descriptive alt text
- **Filename:** Use descriptive, keyword-rich names (hyphen-separated)
  - ✅ Good: `diabetes-management-ai-platform.jpg`
  - ❌ Bad: `image001.jpg`, `IMG_1234.jpg`
- **Lazy Loading:** Already implemented in blog template

### Social Media Preview
Test image previews on:
- Twitter Card Validator: https://cards-dev.twitter.com/validator
- Facebook Sharing Debugger: https://developers.facebook.com/tools/debug/
- LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/

---

## 🚀 Creating the Launch Image (Step-by-Step)

### Option 1: Canva (Easiest)
1. Go to https://canva.com
2. Create account (free tier is fine)
3. Click "Create a design" → "Custom size" → 1200 x 630 px
4. Search templates: "Technology Launch" or "Health Tech"
5. Customize:
   - Change colors to medical blue (#2563eb) and green (#10b981)
   - Add text: "My Health Gheware" and "AI-Powered Diabetes Management"
   - Search elements: "glucose monitor", "AI circuit", "health chart"
   - Add gradients (Elements → Gradient)
6. Download as JPG (high quality)
7. Save to: `/src/blog/assets/images/health-gheware-launch.jpg`

### Option 2: Figma (Professional)
1. Create new frame: 1200 x 630 px
2. Add gradient background (blue to teal)
3. Import or create health tech visuals
4. Add typography (Inter font, bold)
5. Export as JPG at 2x for retina displays
6. Compress using TinyPNG or similar

### Option 3: AI Generation (Quick but requires refinement)
1. Use Midjourney or DALL-E 3
2. Prompt: "Professional medical technology hero image for diabetes management app, glucose monitoring device, AI neural network visualization, modern blue gradient background, clean healthcare aesthetic, 1200x630 ratio, web banner"
3. Generate multiple variations
4. Select best option
5. Refine in Canva/Figma if needed
6. Add text overlays manually

---

## 📦 Future Images Needed (Priority Order)

### Month 1 (Next 4 Weeks)
1. ✅ `health-gheware-launch.jpg` - Launch announcement (COMPLETED - Nov 6, 2025)
2. ⚠️ `time-in-range-guide.jpg` - Post 2: Educational foundation (NEXT PRIORITY)
3. ⚠️ `sleep-blood-sugar.jpg` - Post 3: Sleep-glucose connection
4. ⚠️ `diabetes-101.jpg` - Post 4: Beginner's guide
5. ⚠️ `improve-tir.jpg` - Post 5: 7 ways to improve TIR

### Month 2 (Weeks 5-8)
6. ⚠️ `glycemic-variability.jpg` - Advanced diabetes metrics
7. ⚠️ `ai-health-analysis.jpg` - AI health data analysis
8. ⚠️ `meal-timing-glucose.jpg` - Nutrition and glucose
9. ⚠️ `exercise-diabetes.jpg` - Fitness and diabetes
10. ⚠️ `sleep-habits.jpg` - Sleep optimization

### Month 3 (Weeks 9-12)
11. ⚠️ `success-story.jpg` - Case study template
12. ⚠️ `health-gheware-vs-cgm-apps.jpg` - Comparison post
13. ⚠️ `diabetes-management-routine.jpg` - Lifestyle integration

---

## 🎯 Image Performance Tracking

Track which hero images perform best:
- Click-through rates (blog card → full post)
- Social media engagement (shares, likes)
- Time on page (does image match content expectation?)
- Bounce rate (too generic or misleading?)

**Tools:**
- Google Analytics (blog traffic)
- Social media analytics (engagement rates)
- A/B test different image styles

---

## 💡 Design Inspiration Sources

**Health Tech Examples:**
- Apple Health app imagery
- Google Fit promotional materials
- Dexcom CGM marketing
- Abbott Freestyle Libre branding
- Oura Ring visuals

**AI/Tech Examples:**
- OpenAI branding
- Anthropic Claude visuals
- Modern SaaS hero images
- Tech startup launches

**Medical/Healthcare:**
- Professional medical journals
- Healthcare app store screenshots
- Medical device company websites
- Diabetes foundation materials

---

## ⚠️ Important Reminders

### Medical Accuracy
- Use real CGM device imagery (or generic representations)
- Don't show fake data or misleading glucose readings
- Avoid sensational or scary medical imagery
- No before/after body transformations (compliance issue)

### Brand Consistency
- Every image should be recognizable as "Health Gheware"
- Consistent color scheme across all posts
- Similar visual style (gradients, modern, clean)
- Professional medical aesthetic

### Legal/Compliance
- Use licensed images or create original
- No copyrighted medical device images without permission
- Include medical disclaimer in blog post (not just image)
- Don't imply medical claims or guaranteed results

---

## 📞 Action Items

### ✅ Completed
1. ✅ **Created `health-gheware-launch.jpg`** - November 6, 2025
   - Professional gradient design with data visualization elements
   - 1200x630px, 54.7KB optimized
   - Matches existing blog hero image style
   - Reusable Python script created for future images

### Immediate (Next Priority)
2. ⚠️ **Create `time-in-range-guide.jpg`** for Post 2
   - Use the same style as launch image
   - Focus on TIR visualization (pie chart or gauge)
   - Include target range indicators (70-180 mg/dL)

### This Week
3. Create images for Posts 3 & 4
   - `sleep-blood-sugar.jpg` - Sleep-glucose correlation visualization
   - `diabetes-101.jpg` - Educational foundation image
4. Refine image creation script for different blog post types
5. Create variations of network/correlation patterns

### This Month
6. Design all remaining Month 1 images (Posts 2-5)
7. Test image performance (click-through rates, social shares)
8. Gather user feedback on image style and clarity
9. Create image templates for each blog post category

---

**Document Created:** November 6, 2025
**Last Updated:** November 6, 2025
**Status:** ✅ Launch image completed, ready for Post 2 image
**Priority:** MEDIUM - Post 2 image needed for next publication

**Hero Image Creator:** Python/PIL script at `marketing/create-health-hero.py`
**Contact:** Rajesh Gheware | rajesh@gheware.com
