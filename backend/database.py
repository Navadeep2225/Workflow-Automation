"""
database.py
===========
Handles SQLite database connection management and automatic database schema initialization.
"""

import os
import sqlite3
import config

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Configures sqlite3.Row to access database columns by name (like a dictionary).
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Creates the database directory, database file, and required tables automatically
    if they do not already exist.
    """
    # Create the 'database' directory if it doesn't exist
    if not os.path.exists(config.DATABASE_DIR):
        os.makedirs(config.DATABASE_DIR)
        print(f"[INFO] Created database directory at: {config.DATABASE_DIR}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT NOT NULL UNIQUE,
            department TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Employee'
        )
    ''')

    # 2. Create 'leave_requests' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            ai_decision TEXT,
            confidence TEXT,
            ai_reason TEXT,
            manager_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully with tables 'users' and 'leave_requests'.")
