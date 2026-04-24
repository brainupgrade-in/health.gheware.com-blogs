import os
from pypdf import PdfReader, PdfWriter

OUTPUT_FILE = '/home/rajesh/health.gheware.com/assets/pdfs/The_Complete_Indian_Diabetes_Handbook.pdf'
SOURCE_DIR = '/home/rajesh/health.gheware.com/assets/pdfs'

ORDERED_FILES = [
    'mission-pages.pdf',
    'indian-diabetic-foods-gi-guide.pdf',
    'carb-counting-guide.pdf',
    'cgm-cheat-sheet.pdf',
    'diabetes-medication-guide.pdf',
    'morning-routine-checklist.pdf',
    'indian-breakfast-recipes.pdf',
    'Diabetes-Friendly-Indian-Breakfast-Recipes.pdf',
    'prediabetes-reversal-meal-plan.pdf',
    '7-day-indian-diabetes-meal-plan.pdf',
    'diwali-sweet-alternatives.pdf',
    'exercise-and-yoga.pdf',
    'sleep-blood-sugar-tracker.pdf',
    '30-day-blood-sugar-journal.pdf',
    'doctor-visit-checklist.pdf',
    'diabetes-emergency-guide.pdf'
]

writer = PdfWriter()
total_pages = 0

print("Assembling 'The Complete Indian Diabetes Handbook'...")

for filename in ORDERED_FILES:
    filepath = os.path.join(SOURCE_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filename} not found. Skipping.")
        continue
    
    print(f"Processing {filename}...")
    reader = PdfReader(filepath)
    for page in reader.pages:
        writer.add_page(page)
        total_pages += 1

# Add basic metadata
writer.add_metadata({
    "/Title": "The Complete Indian Diabetes Handbook",
    "/Author": "Dr. Rajesh Gheware",
    "/Subject": "Diabetes Management for Indians",
    "/Creator": "Health Gheware (NotebookLM)",
})

with open(OUTPUT_FILE, "wb") as output_pdf:
    writer.write(output_pdf)

print(f"\n✅ Assembly Complete!")
print(f"Total Pages: {total_pages}")
print(f"Saved to: {OUTPUT_FILE}")
