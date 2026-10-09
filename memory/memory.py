"""Long-term memory in SQLite (events table). Short-term memory lives in st.session_state."""
import datetime as dt
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "studentpilot.db")
last_error = ""


def _conn():
    return sqlite3.connect(DB)


def init():
    global last_error
    try:
        with _conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                      "ts TEXT, student TEXT, kind TEXT, detail TEXT)")
    except sqlite3.Error as e:
        last_error = f"Database error: {e}"


def add(student, kind, detail):
    """kind: goal | preference | weak_area | score | completed | recommendation"""
    global last_error
    try:
        with _conn() as c:
            c.execute("INSERT INTO events(ts,student,kind,detail) VALUES(?,?,?,?)",
                      (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), student, kind, detail))
        return True
    except sqlite3.Error as e:
        last_error = f"Database error: {e}"
        return False


def fetch(student, kind=None, limit=100):
    global last_error
    try:
        with _conn() as c:
            q, p = "SELECT ts,kind,detail FROM events WHERE student=?", [student]
            if kind:
                q += " AND kind=?"
                p.append(kind)
            rows = c.execute(q + " ORDER BY id DESC LIMIT ?", p + [limit]).fetchall()
        return [{"time": r[0], "kind": r[1], "detail": r[2]} for r in rows]
    except sqlite3.Error as e:
        last_error = f"Database error: {e}"
        return []


def clear(student):
    try:
        with _conn() as c:
            c.execute("DELETE FROM events WHERE student=?", (student,))
    except sqlite3.Error:
        pass
