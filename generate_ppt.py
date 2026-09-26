from pptx import Presentation
from pptx.util import Inches

prs = Presentation()

# Slide 1: Title Slide
slide1 = prs.slides.add_slide(prs.slide_layouts[0])
slide1.shapes.title.text = "Bank Locker Rent and Agreement Renewal Tracker"
slide1.placeholders[1].text = "Project Code: 25CC3071-P019 | Branch Banking\nTeam Members: [Your Name], [Teammate Name]\nInstitution: Koneru Lakshmaiah Education Foundation (KLEF)"

# Slide 2: Problem Statement
slide2 = prs.slides.add_slide(prs.slide_layouts[1])
slide2.shapes.title.text = "The Exact Problem Statement"
tf2 = slide2.placeholders[1].text_frame
tf2.text = "Domain: Branch Banking\nTeam Size: 1 team · T019 · 3 students\n\nUse Cases Required:"
p = tf2.add_paragraph()
p.text = "Track locker allotment, rent due and renewal dates"
p.level = 1
p = tf2.add_paragraph()
p.text = "Generate rent-due notices and auto-debit files"
p.level = 1
p = tf2.add_paragraph()
p.text = "\nBottlenecks Students May Encounter:"
p.level = 0
p = tf2.add_paragraph()
p.text = "Locker sizes have different rent slabs"
p.level = 1
p = tf2.add_paragraph()
p.text = "Joint locker holders and nominee updates"
p.level = 1

# Slide 3: Implementing the Use Cases
slide3 = prs.slides.add_slide(prs.slide_layouts[1])
slide3.shapes.title.text = "Implementing the Use Cases"
tf3 = slide3.placeholders[1].text_frame
tf3.text = "Use Case 1: Track locker allotment, rent due, and renewal dates"
p = tf3.add_paragraph()
p.text = "Dashboard built using HTML and FastAPI."
p.level = 1
p = tf3.add_paragraph()
p.text = "Captures customer details, dates, and saves to SQLite."
p.level = 1
p = tf3.add_paragraph()
p.text = "\nUse Case 2: Generate rent-due notices and auto-debit files"
p.level = 0
p = tf3.add_paragraph()
p.text = "'Export Auto-Debit CSV' function built."
p.level = 1
p = tf3.add_paragraph()
p.text = "Queries SQLite for lockers overdue or due in 30 days."
p.level = 1
p = tf3.add_paragraph()
p.text = "Exports filtered list to CSV for batch processing."
p.level = 1

# Slide 4: Solving the Bottlenecks
slide4 = prs.slides.add_slide(prs.slide_layouts[1])
slide4.shapes.title.text = "Solving the Bottlenecks"
tf4 = slide4.placeholders[1].text_frame
tf4.text = "Bottleneck 1: Locker sizes have different rent slabs"
p = tf4.add_paragraph()
p.text = "Solution: Removed manual rent entry. User selects size via dropdown. Python backend assigns correct rent (Small=1500, Medium=3000, Large=5000)."
p.level = 1
p = tf4.add_paragraph()
p.text = "\nBottleneck 2: Joint locker holders and nominee updates"
p.level = 0
p = tf4.add_paragraph()
p.text = "Solution: Dedicated Edit function. Runs SQL UPDATE to overwrite specific fields without deleting the primary record."
p.level = 1

# Slide 5: Architecture Flowchart
slide5 = prs.slides.add_slide(prs.slide_layouts[1])
slide5.shapes.title.text = "Architecture Flowchart"
tf5 = slide5.placeholders[1].text_frame
tf5.text = "1. Adding a Locker (Data Input)"
p = tf5.add_paragraph()
p.text = "UI Form -> POST Request -> FastAPI -> SQL INSERT -> SQLite Database"
p.level = 1
p = tf5.add_paragraph()
p.text = "\n2. Updating Nominees (Data Edit)"
p.level = 0
p = tf5.add_paragraph()
p.text = "UI Edit Form -> POST Request -> FastAPI -> SQL UPDATE -> SQLite Database"
p.level = 1
p = tf5.add_paragraph()
p.text = "\n3. Auto-Debit Generation (Data Output)"
p.level = 0
p = tf5.add_paragraph()
p.text = "UI Click Export -> GET Request -> FastAPI Date Filter -> SQL SELECT -> CSV Download"
p.level = 1

# Slide 6: Technology Stack
slide6 = prs.slides.add_slide(prs.slide_layouts[1])
slide6.shapes.title.text = "Technology Stack"
tf6 = slide6.placeholders[1].text_frame
tf6.text = "Client / Frontend:"
p = tf6.add_paragraph()
p.text = "HTML5 (Structure and forms)"
p.level = 1
p = tf6.add_paragraph()
p.text = "Tailwind CSS (Simple, fast styling)"
p.level = 1
p = tf6.add_paragraph()
p.text = "Jinja2 Templating (Injects database rows directly into the HTML table)"
p.level = 1
p = tf6.add_paragraph()
p.text = "\nServer / Backend:"
p.level = 0
p = tf6.add_paragraph()
p.text = "Python"
p.level = 1
p = tf6.add_paragraph()
p.text = "FastAPI (Lightweight routing and date logic)"
p.level = 1
p = tf6.add_paragraph()
p.text = "\nStorage / Database:"
p.level = 0
p = tf6.add_paragraph()
p.text = "SQLite (Zero-configuration, relational database stored in a local .db file)"
p.level = 1

# Save the presentation
prs.save("Bank_Locker_Tracker_PBL.pptx")
print("Presentation generated successfully: Bank_Locker_Tracker_PBL.pptx")
