from fastapi import FastAPI, Request, Form, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, StreamingResponse
import sqlite3
from datetime import date, datetime
import io
import csv

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DB_FILE = "lockers.db"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# Real-world feature: Late Fee
LATE_FEE_PENALTY = 500 
RENT_SLABS = {"Small": 1500, "Medium": 3000, "Large": 5000}

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        # 1. Active Lockers Table
        conn.execute('''CREATE TABLE IF NOT EXISTS lockers (
            locker_no TEXT PRIMARY KEY,
            primary_holder TEXT,
            joint_holder TEXT,
            nominee TEXT,
            size TEXT,
            rent INTEGER,
            due_date TEXT
        )''')
        # 2. NEW: Historical Audit Trail Table
        conn.execute('''CREATE TABLE IF NOT EXISTS locker_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            locker_no TEXT,
            primary_holder TEXT,
            joint_holder TEXT,
            nominee TEXT,
            surrender_date TEXT
        )''')
        # 3. NEW: System Logs
        conn.execute('''CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            description TEXT
        )''')
init_db()

def log_action(action: str, description: str):
    with sqlite3.connect(DB_FILE) as conn:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO system_logs (timestamp, action, description) VALUES (?, ?, ?)", (now_str, action, description))

def verify_login(auth_token: str = Cookie(None)):
    return auth_token == "logged_in"

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
def login_submit(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="auth_token", value="logged_in")
        return response
    return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("auth_token")
    return response

@app.get("/")
def read_root(request: Request, search: str = "", auth_token: str = Cookie(None)):
    if not verify_login(auth_token): 
        return templates.TemplateResponse(request=request, name="welcome.html")

    today_str = str(date.today())
    today_date = date.today()

    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        if search:
            query = "SELECT * FROM lockers WHERE primary_holder LIKE ? OR locker_no LIKE ? ORDER BY due_date ASC"
            lockers_db = conn.execute(query, (f"%{search}%", f"%{search}%")).fetchall()
        else:
            lockers_db = conn.execute("SELECT * FROM lockers ORDER BY due_date ASC").fetchall()
            
        logs_db = conn.execute("SELECT * FROM system_logs ORDER BY id DESC LIMIT 5").fetchall()

    lockers = []
    total_revenue = 0
    overdue_count = 0

    for row in lockers_db:
        locker = dict(row)
        due = datetime.strptime(locker["due_date"], "%Y-%m-%d").date()
        days_overdue = (today_date - due).days
        
        locker["has_penalty"] = False
        if days_overdue > 30:
            locker["rent"] += LATE_FEE_PENALTY
            locker["has_penalty"] = True
            
        if days_overdue > 0:
            overdue_count += 1
            
        total_revenue += locker["rent"]
        lockers.append(locker)

    analytics = {
        "total_lockers": len(lockers_db),
        "overdue_count": overdue_count,
        "total_revenue": total_revenue
    }
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "lockers": lockers, 
            "today": today_str,
            "search": search,
            "analytics": analytics,
            "logs": logs_db
        }
    )

@app.post("/add")
def add_locker(
    auth_token: str = Cookie(None),
    locker_no: str = Form(...),
    primary_holder: str = Form(...),
    joint_holder: str = Form(""),
    nominee: str = Form(""),
    size: str = Form(...),
    due_date: str = Form(...)
):
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    rent = RENT_SLABS.get(size, 1500)
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO lockers VALUES (?, ?, ?, ?, ?, ?, ?)",
                (locker_no, primary_holder, joint_holder, nominee, size, rent, due_date)
            )
        log_action("ADD", f"Locker {locker_no} allotted to {primary_holder}")
    except sqlite3.IntegrityError:
        pass 
    return RedirectResponse(url="/", status_code=303)

@app.post("/remove/{locker_no}")
def remove_locker(locker_no: str, auth_token: str = Cookie(None)):
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    
    today_str = str(date.today())
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        # Step 1: Get the current customer data
        locker = conn.execute("SELECT * FROM lockers WHERE locker_no = ?", (locker_no,)).fetchone()
        
        if locker:
            # Step 2: Copy their details into the History table
            conn.execute(
                "INSERT INTO locker_history (locker_no, primary_holder, joint_holder, nominee, surrender_date) VALUES (?, ?, ?, ?, ?)",
                (locker["locker_no"], locker["primary_holder"], locker["joint_holder"], locker["nominee"], today_str)
            )
            # Step 3: Free up the active locker
            conn.execute("DELETE FROM lockers WHERE locker_no = ?", (locker_no,))
            
    if locker:
        log_action("REMOVE", f"Locker {locker_no} surrendered by {locker['primary_holder']}")
        
    return RedirectResponse(url="/", status_code=303)

@app.get("/export")
def export_autodebit(auth_token: str = Cookie(None)):
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    today = str(date.today())
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        target_lockers = conn.execute(
            "SELECT * FROM lockers WHERE due_date <= date(?, '+30 days')", (today,)
        ).fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Locker_Number", "Primary_Holder", "Rent_Amount", "Due_Date", "Status"])
    for row in target_lockers:
        status = "OVERDUE" if row["due_date"] < today else "DUE SOON"
        writer.writerow([row["locker_no"], row["primary_holder"], row["rent"], row["due_date"], status])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=autodebit_{today}.csv"}
    )

# --- NEW HISTORY FEATURE ---
@app.get("/history")
def view_history(request: Request, auth_token: str = Cookie(None)):
    # Protected by the same admin password!
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        history_records = conn.execute("SELECT * FROM locker_history ORDER BY surrender_date DESC").fetchall()
        
    return templates.TemplateResponse(request=request, name="history.html", context={"records": history_records})

# --- NEW EDIT FEATURES ---

@app.get("/edit/{locker_no}")
def edit_page(locker_no: str, request: Request, auth_token: str = Cookie(None)):
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        locker = conn.execute("SELECT * FROM lockers WHERE locker_no = ?", (locker_no,)).fetchone()
        
    if not locker:
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse(request=request, name="edit.html", context={"locker": dict(locker)})

@app.post("/edit/{locker_no}")
def update_locker(
    locker_no: str,
    joint_holder: str = Form(""),
    nominee: str = Form(""),
    auth_token: str = Cookie(None)
):
    if not verify_login(auth_token): return RedirectResponse(url="/login", status_code=303)
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "UPDATE lockers SET joint_holder = ?, nominee = ? WHERE locker_no = ?",
            (joint_holder, nominee, locker_no)
        )
    log_action("EDIT", f"Locker {locker_no} details updated")
    return RedirectResponse(url="/", status_code=303)

# --- NEW CLIENT PORTAL & AGREEMENT FEATURES ---

@app.get("/client-login")
def client_login_page(request: Request):
    return templates.TemplateResponse(request=request, name="client_login.html")

@app.post("/client-login")
def client_login_submit(locker_no: str = Form(...), primary_holder: str = Form(...)):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        locker = conn.execute("SELECT * FROM lockers WHERE locker_no = ? AND primary_holder = ?", (locker_no, primary_holder)).fetchone()
    
    if locker:
        response = RedirectResponse(url="/client-dashboard", status_code=303)
        response.set_cookie(key="client_token", value=locker_no)
        return response
    return RedirectResponse(url="/client-login?error=1", status_code=303)

@app.get("/client-logout")
def client_logout():
    response = RedirectResponse(url="/client-login", status_code=303)
    response.delete_cookie("client_token")
    return response

@app.get("/client-dashboard")
def client_dashboard(request: Request, client_token: str = Cookie(None)):
    if not client_token:
        return RedirectResponse(url="/client-login", status_code=303)
        
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        locker = conn.execute("SELECT * FROM lockers WHERE locker_no = ?", (client_token,)).fetchone()
        
    if not locker:
        response = RedirectResponse(url="/client-login", status_code=303)
        response.delete_cookie("client_token")
        return response
        
    locker_dict = dict(locker)
    due = datetime.strptime(locker_dict["due_date"], "%Y-%m-%d").date()
    days_overdue = (date.today() - due).days
    locker_dict["has_penalty"] = False
    if days_overdue > 30:
        locker_dict["rent"] += LATE_FEE_PENALTY
        locker_dict["has_penalty"] = True
        
    return templates.TemplateResponse(request=request, name="client_dashboard.html", context={"locker": locker_dict, "today": str(date.today())})

@app.get("/agreement/{locker_no}")
def view_agreement(locker_no: str, request: Request, auth_token: str = Cookie(None), client_token: str = Cookie(None)):
    if not (verify_login(auth_token) or client_token == locker_no):
        return RedirectResponse(url="/login", status_code=303)
        
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        locker = conn.execute("SELECT * FROM lockers WHERE locker_no = ?", (locker_no,)).fetchone()
        
    if not locker:
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse(request=request, name="agreement.html", context={"locker": dict(locker), "date": str(date.today())})
