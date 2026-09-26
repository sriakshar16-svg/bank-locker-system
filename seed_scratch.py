import sqlite3
from datetime import date, datetime

DB_FILE = "/home/tsriakshar/.gemini/antigravity/scratch/locker_system/lockers.db"

with sqlite3.connect(DB_FILE) as conn:
    conn.execute("DROP TABLE IF EXISTS lockers")
    conn.execute("DROP TABLE IF EXISTS locker_history")
    conn.execute("DROP TABLE IF EXISTS system_logs")
    
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

    test_data = [
        ("A-101", "Rahul Sharma", "Sneha Sharma", "Aryan Sharma", "Small", 1500, "2026-10-15"),
        ("B-205", "Priya Patel", "", "Ravi Patel", "Medium", 3000, "2026-08-01"),
        ("C-310", "Amit Kumar", "Sunita Kumar", "", "Large", 5000, "2027-01-20"),
        ("A-102", "Neha Gupta", "", "", "Small", 1500, "2026-09-10"),
        ("B-206", "Vikram Singh", "Pooja Singh", "Raj Singh", "Medium", 3000, "2026-12-10")
    ]

    for data in test_data:
        conn.execute("INSERT INTO lockers VALUES (?, ?, ?, ?, ?, ?, ?)", data)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO system_logs (timestamp, action, description) VALUES (?, ?, ?)", (now_str, "SYSTEM_RESET", "Database wiped and seeded with 5 test accounts."))

print("Scratch DB Seeded!")
