import sqlite3
import os
from datetime import datetime

DB_PATH = "history.db"

def init_db():
    """
    Initializes the SQLite database and creates the history table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the history table, extending the basic structure to be rich and dashboard-ready
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER NOT NULL,
        date TEXT NOT NULL,
        filename TEXT,
        job_title TEXT,
        matched_skills TEXT,
        missing_skills TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def save_analysis(score: int, filename: str, job_title: str, matched: list, missing: list):
    """
    Saves a resume analysis entry to the history table.
    """
    # Ensure DB is initialized
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    matched_str = ", ".join(matched)
    missing_str = ", ".join(missing)
    
    cursor.execute("""
    INSERT INTO history (score, date, filename, job_title, matched_skills, missing_skills)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (score, current_time, filename, job_title, matched_str, missing_str))
    
    conn.commit()
    conn.close()

def get_history_records() -> list:
    """
    Fetches all historical records from the database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, score, date, filename, job_title, matched_skills, missing_skills FROM history ORDER BY date DESC")
    records = cursor.fetchall()
    
    conn.close()
    return records

def clear_db():
    """
    Truncates the history table to clear analysis history.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
