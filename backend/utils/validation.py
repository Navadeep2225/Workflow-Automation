"""
validation.py
=============
Utility functions for validating incoming HTTP request JSON payloads.
Performs checks for missing fields, empty inputs, invalid date formats, and logical date ranges.
"""

from datetime import datetime

def validate_registration_data(data):
    """
    Validates user registration input data.
    Returns (is_valid: bool, error_message: str or None)
    """
    if not data or not isinstance(data, dict):
        return False, "Invalid JSON input payload"

    required_fields = ['name', 'employee_id', 'department', 'email', 'password']
    
    # Check for missing or empty required fields
    for field in required_fields:
        if field not in data or not str(data.get(field, '')).strip():
            return False, f"Missing or empty field: {field}"

    return True, None


def validate_login_data(data):
    """
    Validates user login input data.
    Returns (is_valid: bool, error_message: str or None)
    """
    if not data or not isinstance(data, dict):
        return False, "Invalid JSON input payload"

    if 'email' not in data or not str(data.get('email', '')).strip():
        return False, "Missing or empty field: email"

    if 'password' not in data or not str(data.get('password', '')).strip():
        return False, "Missing or empty field: password"

    return True, None


def validate_leave_request_data(data):
    """
    Validates leave submission request data.
    Checks for:
    - Missing employee_id
    - Missing reason
    - Empty fields
    - Invalid date formats (YYYY-MM-DD)
    - End date prior to start date
    Returns (is_valid: bool, error_message: str or None)
    """
    if not data or not isinstance(data, dict):
        return False, "Invalid Input"

    # Specific check for missing or empty employee_id
    if 'employee_id' not in data or not str(data.get('employee_id', '')).strip():
        return False, "Missing Employee ID"

    # Specific check for missing or empty reason
    if 'reason' not in data or not str(data.get('reason', '')).strip():
        return False, "Missing Reason"

    required_fields = ['employee_id', 'leave_type', 'start_date', 'end_date', 'reason']

    # General empty fields check
    for field in required_fields:
        if field not in data or not str(data.get(field, '')).strip():
            return False, f"Invalid Input: {field} cannot be empty"

    start_date_str = str(data['start_date']).strip()
    end_date_str = str(data['end_date']).strip()

    # Date format validation (YYYY-MM-DD)
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, "Invalid Date Format for start_date (expected YYYY-MM-DD)"

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, "Invalid Date Format for end_date (expected YYYY-MM-DD)"

    # End date before start date validation
    if end_date < start_date:
        return False, "End date cannot be before start date"

    return True, None
