import sqlite3
from datetime import datetime

DB = "expenses.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            amount REAL,
            note TEXT,
            tag TEXT,
            receipt_path TEXT,
            is_recurring INTEGER DEFAULT 0,
            recurring_interval TEXT,
            date TEXT,
            language TEXT DEFAULT 'km'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            pin TEXT,
            language TEXT DEFAULT 'km',
            daily_reminder INTEGER DEFAULT 0,
            reminder_time TEXT DEFAULT '20:00',
            budget_limit REAL DEFAULT 0,
            is_logged_in INTEGER DEFAULT 0
        )
    """)

    # បន្ថែម column is_logged_in បើមិនទាន់មាន (សម្រាប់ database ចាស់)
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_logged_in INTEGER DEFAULT 0")
        conn.commit()
    except:
        pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_name TEXT,
            target_amount REAL,
            saved_amount REAL DEFAULT 0,
            deadline TEXT
        )
    """)

    conn.commit()
    conn.close()

# ── User ──────────────────────────────────────────────
def get_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def set_pin(user_id, pin):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET pin=? WHERE user_id=?", (pin, user_id))
    conn.commit()
    conn.close()

def get_pin(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT pin FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# ── Persistent Login ──────────────────────────────────
def set_logged_in(user_id, status: bool):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET is_logged_in=? WHERE user_id=?",
              (1 if status else 0, user_id))
    conn.commit()
    conn.close()

def get_logged_in(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT is_logged_in FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def set_language(user_id, lang):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def get_language(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 'km'

def set_reminder(user_id, enabled, time="20:00"):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET daily_reminder=?, reminder_time=? WHERE user_id=?",
              (1 if enabled else 0, time, user_id))
    conn.commit()
    conn.close()

def set_budget(user_id, amount):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET budget_limit=? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_budget(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT budget_limit FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

# ── Expenses ──────────────────────────────────────────
def add_expense(user_id, category, amount, note, tag="", receipt_path="",
                is_recurring=0, recurring_interval=""):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO expenses
        (user_id, category, amount, note, tag, receipt_path, is_recurring, recurring_interval, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, category, amount, note, tag, receipt_path,
          is_recurring, recurring_interval, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def delete_expense(expense_id, user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    conn.commit()
    conn.close()

def get_today(user_id):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, category, amount, note, tag FROM expenses
        WHERE user_id=? AND date=? ORDER BY id DESC
    """, (user_id, today))
    rows = c.fetchall()
    conn.close()
    return rows

def get_by_date(user_id, date_str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, category, amount, note, tag FROM expenses
        WHERE user_id=? AND date=? ORDER BY id DESC
    """, (user_id, date_str))
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly(user_id, year_month=None):
    if not year_month:
        year_month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT category, SUM(amount) FROM expenses
        WHERE user_id=? AND date LIKE ?
        GROUP BY category ORDER BY SUM(amount) DESC
    """, (user_id, f"{year_month}%"))
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly_total(user_id, year_month=None):
    if not year_month:
        year_month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE user_id=? AND date LIKE ?
    """, (user_id, f"{year_month}%"))
    row = c.fetchone()
    conn.close()
    return row[0] or 0

def get_by_tag(user_id, tag):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, category, amount, note, date FROM expenses
        WHERE user_id=? AND tag=? ORDER BY date DESC LIMIT 20
    """, (user_id, tag))
    rows = c.fetchall()
    conn.close()
    return rows

def get_recurring(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT DISTINCT category, amount, note, recurring_interval FROM expenses
        WHERE user_id=? AND is_recurring=1
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ── Savings Goals ─────────────────────────────────────
def add_goal(user_id, name, target, deadline):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO savings_goals (user_id, goal_name, target_amount, deadline)
        VALUES (?, ?, ?, ?)
    """, (user_id, name, target, deadline))
    conn.commit()
    conn.close()

def get_goals(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, goal_name, target_amount, saved_amount, deadline FROM savings_goals WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def update_goal_savings(goal_id, amount):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE savings_goals SET saved_amount=saved_amount+? WHERE id=?", (amount, goal_id))
    conn.commit()
    conn.close()