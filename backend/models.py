"""
models.py
=========
Contains helper functions for interacting with SQLite database tables (users and leave_requests).
All database functions execute clean SQL queries and return dictionary objects.
"""

from database import get_db_connection

# ==========================================
# USER DATABASE OPERATIONS
# ==========================================

def create_user(name, employee_id, department, email, password, role='Employee'):
    """
    Inserts a new user record into the 'users' table.
    Returns the created user's ID on success.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO users (name, employee_id, department, email, password, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (name, employee_id, department, email, password, role)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_user_by_email(email):
    """
    Retrieves a user record by email.
    Returns a dictionary of user details or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_employee_id(employee_id):
    """
    Retrieves a user record by employee_id.
    Returns a dictionary of user details or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE employee_id = ?', (employee_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# ==========================================
# LEAVE REQUEST DATABASE OPERATIONS
# ==========================================

def create_leave_request(employee_id, leave_type, start_date, end_date, reason):
    """
    Inserts a new leave request record with initial manager_status='Pending'.
    Returns the newly created leave_request ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO leave_requests (employee_id, leave_type, start_date, end_date, reason, manager_status)
        VALUES (?, ?, ?, ?, ?, 'Pending')
        ''',
        (employee_id, leave_type, start_date, end_date, reason)
    )
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id

def update_ai_recommendation(request_id, ai_decision, confidence, ai_reason):
    """
    Updates a leave request record with the AI decision, confidence score, and reasoning.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE leave_requests
        SET ai_decision = ?, confidence = ?, ai_reason = ?
        WHERE id = ?
        ''',
        (ai_decision, confidence, ai_reason, request_id)
    )
    conn.commit()
    conn.close()

def get_leave_request_by_id(request_id):
    """
    Fetches a single leave request record by its primary key ID.
    Returns a dictionary or None if not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leave_requests WHERE id = ?', (request_id,))
    request = cursor.fetchone()
    conn.close()
    return dict(request) if request else None

def get_leave_history_by_employee(employee_id):
    """
    Retrieves all leave requests submitted by a specific employee.
    Ordered by creation date (newest first).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM leave_requests 
        WHERE employee_id = ? 
        ORDER BY created_at DESC
        ''', 
        (employee_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_pending_leave_requests():
    """
    Retrieves all leave requests where manager_status is 'Pending'.
    Ordered by creation date (newest first).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT * FROM leave_requests 
        WHERE manager_status = 'Pending' 
        ORDER BY created_at DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_manager_status(request_id, status):
    """
    Updates manager_status to 'Approved' or 'Rejected' for a given leave request ID.
    Returns True if update succeeded, False if ID was not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE leave_requests
        SET manager_status = ?
        WHERE id = ?
        ''',
        (status, request_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
