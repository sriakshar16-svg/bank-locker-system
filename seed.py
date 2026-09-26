import sqlite3
from datetime import date, datetime, timedelta

DB_FILE = "/home/tsriakshar/Desktop/bank-locker-system/lockers.db"
# Fallback just in case
try:
    conn = sqlite3.connect(DB_FILE)
except:
    DB_FILE = "/home/tsriakshar/.gemini/antigravity/scratch/locker_system/lockers.db"

with sqlite3.connect(DB_FILE) as conn:
    # Wipe the existing tables completely
    conn.execute("DROP TABLE IF EXISTS lockers")
    conn.execute("DROP TABLE IF EXISTS locker_history")
    conn.execute("DROP TABLE IF EXISTS system_logs")
    
    # Recreate the tables
    conn.execute('''CREATE TABLE IF NOT EXISTS lockers (
        locker_no TEXT PRIMARY KEY,
        primary_holder TEXT,
        joint_holder TEXT,
        nominee TEXT,
        size TEXT,
        rent INTEGER,
        due_date TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS locker_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        locker_no TEXT,
        primary_holder TEXT,
        joint_holder TEXT,
        nominee TEXT,
        surrender_date TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        description TEXT
    )''')

    # Seed 5 realistic test lockers
    test_data = [
        ("A-101", "Rahul Sharma", "Sneha Sharma", "Aryan Sharma", "Small", 1500, "2026-10-15"),  # Active
        ("B-205", "Priya Patel", "", "Ravi Patel", "Medium", 3000, "2026-08-01"),            # Very Overdue (Penalty)
        ("C-310", "Amit Kumar", "Sunita Kumar", "", "Large", 5000, "2027-01-20"),            # Active
        ("A-102", "Neha Gupta", "", "", "Small", 1500, "2026-09-10"),                        # Overdue (< 30 days)
        ("B-206", "Vikram Singh", "Pooja Singh", "Raj Singh", "Medium", 3000, "2026-12-10")  # Active
    ]

    for data in test_data:
        conn.execute(
            "INSERT INTO lockers VALUES (?, ?, ?, ?, ?, ?, ?)",
            data
        )

    # Add a system log indicating the database was reset
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO system_logs (timestamp, action, description) VALUES (?, ?, ?)", (now_str, "SYSTEM_RESET", "Database wiped and seeded with 5 test accounts."))

print("Database wiped and seeded successfully!")
