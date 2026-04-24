#!/usr/bin/env python3
"""
Build The Complete Indian Diabetes Handbook
Combines all PDFs + generated HTML pages into one final book PDF

Usage: python3 build_book.py
Output: ../output/The-Complete-Indian-Diabetes-Handbook.pdf
"""

import subprocess
import os
import sys
from pypdf import PdfReader, PdfWriter, PageObject
from pypdf.generic import RectangleObject

# ==============================================================
# Configuration
# ==============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)  # book-project/
PDF_DIR = os.path.dirname(PROJECT_DIR)   # assets/pdfs/
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

# Target page size (matching existing NotebookLM slides)
TARGET_WIDTH = 1376   # pts
TARGET_HEIGHT = 768   # pts

# HTML files to convert to PDF
HTML_FILES = {
    "front-matter": os.path.join(PROJECT_DIR, "front-matter", "front-matter.html"),
    "chapter-intros": os.path.join(PROJECT_DIR, "chapter-intros", "chapter-intros.html"),
    "back-matter": os.path.join(PROJECT_DIR, "back-matter", "back-matter.html"),
}

# Final book assembly order
# Format: (type, source_path, label)
# type: "pdf" = existing PDF, "html_pages" = pages from converted HTML
BOOK_ORDER = [
    # ---- FRONT MATTER (7 pages) ----
    ("html_pages", "front-matter", range(0, 7), "Front Matter"),
    
    # ---- PART I DIVIDER ----
    ("html_pages", "chapter-intros", [0], "Part I Divider"),
    
    # ---- CHAPTER 1: GI Guide ----
    ("html_pages", "chapter-intros", [1], "Chapter 1 Intro"),
    ("pdf", os.path.join(PDF_DIR, "indian-diabetic-foods-gi-guide.pdf"), "Chapter 1: GI Guide"),
    
    # ---- CHAPTER 2: Carb Counting ----
    ("html_pages", "chapter-intros", [2], "Chapter 2 Intro"),
    ("pdf", os.path.join(PDF_DIR, "carb-counting-guide.pdf"), "Chapter 2: Carb Counting"),
    
    # ---- CHAPTER 3: CGM ----
    ("html_pages", "chapter-intros", [3], "Chapter 3 Intro"),
    ("pdf", os.path.join(PDF_DIR, "cgm-cheat-sheet.pdf"), "Chapter 3: CGM Guide"),
    
    # ---- CHAPTER 4: Medications ----
    ("html_pages", "chapter-intros", [4], "Chapter 4 Intro"),
    ("pdf", os.path.join(PDF_DIR, "diabetes-medication-guide.pdf"), "Chapter 4: Medications"),
    
    # ---- PART II DIVIDER ----
    ("html_pages", "chapter-intros", [5], "Part II Divider"),
    
    # ---- CHAPTER 5: Morning Routine ----
    ("html_pages", "chapter-intros", [6], "Chapter 5 Intro"),
    ("pdf", os.path.join(PDF_DIR, "morning-routine-checklist.pdf"), "Chapter 5: Morning Routine"),
    
    # ---- CHAPTER 6: 30 Breakfast Ideas ----
    ("html_pages", "chapter-intros", [7], "Chapter 6 Intro"),
    ("pdf", os.path.join(PDF_DIR, "indian-breakfast-recipes.pdf"), "Chapter 6: Breakfast Ideas"),
    
    # ---- CHAPTER 7: Breakfast Recipes ----
    ("html_pages", "chapter-intros", [8], "Chapter 7 Intro"),
    ("pdf", os.path.join(PDF_DIR, "Diabetes-Friendly-Indian-Breakfast-Recipes.pdf"), "Chapter 7: Breakfast Recipes"),
    
    # ---- CHAPTER 8: Pre-Diabetes Reversal ----
    ("html_pages", "chapter-intros", [9], "Chapter 8 Intro"),
    ("pdf", os.path.join(PDF_DIR, "prediabetes-reversal-meal-plan.pdf"), "Chapter 8: Pre-Diabetes Reversal"),
    
    # ---- CHAPTER 9: 7-Day Meal Plan ----
    ("html_pages", "chapter-intros", [10], "Chapter 9 Intro"),
    ("pdf", os.path.join(PDF_DIR, "7-day-indian-diabetes-meal-plan.pdf"), "Chapter 9: 7-Day Meal Plan"),
    
    # ---- CHAPTER 10: Festival Sweets ----
    ("html_pages", "chapter-intros", [11], "Chapter 10 Intro"),
    ("pdf", os.path.join(PDF_DIR, "diwali-sweet-alternatives.pdf"), "Chapter 10: Festival Sweets"),
    
    # ---- PART III DIVIDER ----
    ("html_pages", "chapter-intros", [12], "Part III Divider"),
    
    # ---- CHAPTER 11: Sleep Tracker ----
    ("html_pages", "chapter-intros", [13], "Chapter 11 Intro"),
    ("pdf", os.path.join(PDF_DIR, "sleep-blood-sugar-tracker.pdf"), "Chapter 11: Sleep Tracker"),
    
    # ---- CHAPTER 12: Blood Sugar Journal ----
    ("html_pages", "chapter-intros", [14], "Chapter 12 Intro"),
    ("pdf", os.path.join(PDF_DIR, "30-day-blood-sugar-journal.pdf"), "Chapter 12: Blood Sugar Journal"),
    
    # ---- CHAPTER 13: Doctor Visit ----
    ("html_pages", "chapter-intros", [15], "Chapter 13 Intro"),
    ("pdf", os.path.join(PDF_DIR, "doctor-visit-checklist.pdf"), "Chapter 13: Doctor Visit"),
    
    # ---- BACK MATTER (5 pages) ----
    ("html_pages", "back-matter", range(0, 5), "Back Matter"),
]


def html_to_pdf(html_path, output_path):
    """Convert HTML to PDF using Chrome headless."""
    abs_html = os.path.abspath(html_path)
    abs_out = os.path.abspath(output_path)
    
    cmd = [
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-software-rasterizer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_out}",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        f"--window-size={TARGET_WIDTH},{TARGET_HEIGHT}",
        f"file://{abs_html}"
    ]
    
    print(f"  Converting: {os.path.basename(html_path)} → {os.path.basename(output_path)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    if result.returncode != 0:
        print(f"  ⚠️  Chrome stderr: {result.stderr[:200]}")
    
    if os.path.exists(abs_out):
        reader = PdfReader(abs_out)
        print(f"  ✅ Generated {len(reader.pages)} pages")
        return True
    else:
        print(f"  ❌ Failed to generate PDF")
        return False


def scale_page_to_target(page):
    """Scale a page to match the target dimensions."""
    src_w = float(page.mediabox.width)
    src_h = float(page.mediabox.height)
    
    # If already the right size, skip
    if abs(src_w - TARGET_WIDTH) < 5 and abs(src_h - TARGET_HEIGHT) < 5:
        return page
    
    # Calculate scale to fit
    scale_x = TARGET_WIDTH / src_w
    scale_y = TARGET_HEIGHT / src_h
    scale = min(scale_x, scale_y)  # Fit within target
    
    # Create new page at target size
    new_page = PageObject.create_blank_page(width=TARGET_WIDTH, height=TARGET_HEIGHT)
    
    # Center the scaled content
    tx = (TARGET_WIDTH - src_w * scale) / 2
    ty = (TARGET_HEIGHT - src_h * scale) / 2
    
    new_page.merge_scaled_translated_page(page, scale=scale, tx=tx, ty=ty)
    
    return new_page


def build_book():
    """Main build function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("📚 Building: The Complete Indian Diabetes Handbook")
    print("=" * 60)
    
    # Step 1: Convert all HTML files to PDF
    print("\n📄 Step 1: Converting HTML to PDF...")
    converted_pdfs = {}
    
    for key, html_path in HTML_FILES.items():
        output_path = os.path.join(OUTPUT_DIR, f"_{key}.pdf")
        if html_to_pdf(html_path, output_path):
            converted_pdfs[key] = output_path
        else:
            print(f"  ❌ FATAL: Could not convert {key}")
            sys.exit(1)
    
    # Step 2: Load all converted PDFs
    print("\n📖 Step 2: Loading PDF pages...")
    html_readers = {}
    for key, path in converted_pdfs.items():
        html_readers[key] = PdfReader(path)
        print(f"  Loaded {key}: {len(html_readers[key].pages)} pages")
    
    # Step 3: Assemble the book
    print("\n🔨 Step 3: Assembling the book...")
    writer = PdfWriter()
    total_pages = 0
    
    for entry in BOOK_ORDER:
        entry_type = entry[0]
        
        if entry_type == "html_pages":
            _, key, page_indices, label = entry
            reader = html_readers[key]
            for idx in page_indices:
                if idx < len(reader.pages):
                    page = reader.pages[idx]
                    scaled = scale_page_to_target(page)
                    writer.add_page(scaled)
                    total_pages += 1
                else:
                    print(f"  ⚠️  Page {idx} not found in {key} (only {len(reader.pages)} pages)")
            print(f"  ✅ {label}: {len(list(page_indices))} page(s)")
            
        elif entry_type == "pdf":
            _, pdf_path, label = entry
            if not os.path.exists(pdf_path):
                print(f"  ❌ Missing: {pdf_path}")
                continue
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                scaled = scale_page_to_target(page)
                writer.add_page(scaled)
                total_pages += 1
            print(f"  ✅ {label}: {len(reader.pages)} page(s)")
    
    # Step 4: Add metadata
    print("\n📝 Step 4: Adding metadata...")
    writer.add_metadata({
        "/Title": "The Complete Indian Diabetes Handbook",
        "/Author": "Dr. Rajesh Gheware",
        "/Subject": "Diabetes Management for Indians",
        "/Keywords": "diabetes, Indian food, blood sugar, glycemic index, meal plan, recipes",
        "/Creator": "Health Gheware",
        "/Producer": "Health Gheware Book Builder",
    })
    
    # Step 5: Write final PDF
    output_file = os.path.join(OUTPUT_DIR, "The-Complete-Indian-Diabetes-Handbook.pdf")
    print(f"\n💾 Step 5: Writing final book...")
    
    with open(output_file, "wb") as f:
        writer.write(f)
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    
    print(f"\n{'=' * 60}")
    print(f"✅ BOOK BUILT SUCCESSFULLY!")
    print(f"{'=' * 60}")
    print(f"📖 Total Pages: {total_pages}")
    print(f"💾 File Size: {file_size:.1f} MB")
    print(f"📁 Output: {output_file}")
    print(f"{'=' * 60}")
    
    return output_file


if __name__ == "__main__":
    build_book()
