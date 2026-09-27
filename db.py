
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "planner.db"

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hourly_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_date TEXT NOT NULL,
            hour TEXT NOT NULL,
            task_text TEXT NOT NULL DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(task_date, hour)
        )
    """)
    conn.commit()
    conn.close()

def get_hourly_tasks(task_date):
    conn = connect()
    rows = conn.execute("""
        SELECT task_date, hour, task_text, done
        FROM hourly_tasks
        WHERE task_date=?
        ORDER BY hour ASC
    """, (task_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_hourly_task(task_date, hour, task_text, done=0):
    conn = connect()
    conn.execute("""
        INSERT INTO hourly_tasks(task_date, hour, task_text, done)
        VALUES(?,?,?,?)
        ON CONFLICT(task_date, hour)
        DO UPDATE SET
            task_text=excluded.task_text,
            done=excluded.done,
            updated_at=CURRENT_TIMESTAMP
    """, (task_date, hour, task_text, done))
    conn.commit()
    conn.close()

def toggle_hourly_task(task_date, hour, done):
    conn = connect()

    existing = conn.execute("""
        SELECT task_text
        FROM hourly_tasks
        WHERE task_date=? AND hour=?
    """, (task_date, hour)).fetchone()

    if existing:
        conn.execute("""
            UPDATE hourly_tasks
            SET done=?, updated_at=CURRENT_TIMESTAMP
            WHERE task_date=? AND hour=?
        """, (done, task_date, hour))
    else:
        conn.execute("""
            INSERT INTO hourly_tasks(task_date, hour, task_text, done)
            VALUES(?,?,?,?)
        """, (task_date, hour, "", done))

    conn.commit()
    conn.close()

def delete_hourly_task(task_date, hour):
    conn = connect()
    conn.execute("""
        DELETE FROM hourly_tasks
        WHERE task_date=? AND hour=?
    """, (task_date, hour))
    conn.commit()
    conn.close()

def get_month_report(year, month):
    prefix = f"{year:04d}-{month:02d}"
    conn = connect()
    rows = conn.execute("""
        SELECT task_date, hour, task_text, done
        FROM hourly_tasks
        WHERE task_date LIKE ?
          AND TRIM(task_text) != ''
        ORDER BY task_date ASC, hour ASC
    """, (prefix + "%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
