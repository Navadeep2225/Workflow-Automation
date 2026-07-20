`"""
routes.py
=========
Defines REST API endpoints for User Registration, Login, Leave Submission,
Leave History, Manager Pending View, and Manager Approval/Rejection.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from models import (
    create_user,
    get_user_by_email,
    get_user_by_employee_id,
    create_leave_request,
    update_ai_recommendation,
    get_leave_history_by_employee,
    get_pending_leave_requests,
    update_manager_status,
    get_leave_request_by_id
)
from utils.validation import (
    validate_registration_data,
    validate_login_data,
    validate_leave_request_data
)
from ai_connector import analyze_leave

# Blueprint for grouping API endpoints cleanly
api_blueprint = Blueprint('api', __name__)

# ==========================================
# 1. USER REGISTRATION
# ==========================================
@api_blueprint.route('/register', methods=['POST'])
def register():
    """
    POST /register
    Registers a new user (Employee or Manager).
    """
    try:
        data = request.get_json()

        # Validate input data
        is_valid, error_msg = validate_registration_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        name = data.get('name').strip()
        employee_id = data.get('employee_id').strip()
        department = data.get('department').strip()
        email = data.get('email').strip().lower()
        password = data.get('password').strip()
        role = data.get('role', 'Employee').strip()

        # Create user record in database
        user_id = create_user(name, employee_id, department, email, password, role)

        return jsonify({
            "message": "User Registered Successfully",
            "user_id": user_id,
            "employee_id": employee_id,
            "role": role
        }), 201

    except sqlite3.IntegrityError:
        # Occurs if email or employee_id already exists in table
        return jsonify({"error": "Employee ID or Email already registered"}), 400
    except Exception as e:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 2. USER LOGIN
# ==========================================
@api_blueprint.route('/login', methods=['POST'])
def login():
    """
    POST /login
    Authenticates user and returns role.
    """
    try:
        data = request.get_json()

        # Validate login input data
        is_valid, error_msg = validate_login_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        email = data.get('email').strip().lower()
        password = data.get('password').strip()

        # Fetch user by email
        user = get_user_by_email(email)

        if not user or user['password'] != password:
            return jsonify({"error": "Invalid Email or Password"}), 401

        return jsonify({
            "message": "Login Successful",
            "role": user['role']
        }), 200

    except Exception:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 3. SUBMIT LEAVE REQUEST (WITH AI INTEGRATION)
# ==========================================
@api_blueprint.route('/leave', methods=['POST'])
def submit_leave():
    """
    POST /leave
    Flow:
    1. Validate request
    2. Store in database
    3. Send to AI Module
    4. Receive AI recommendation
    5. Update database with recommendation
    6. Return recommendation response to frontend
    """
    try:
        data = request.get_json()

        # Step 1: Validate request input
        is_valid, error_msg = validate_leave_request_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        employee_id = data.get('employee_id').strip()
        leave_type = data.get('leave_type').strip()
        start_date = data.get('start_date').strip()
        end_date = data.get('end_date').strip()
        reason = data.get('reason').strip()

        # Check if employee exists
        employee = get_user_by_employee_id(employee_id)
        if not employee:
            return jsonify({"error": "Employee Not Found"}), 404

        # Step 2: Store leave request in SQLite database
        request_id = create_leave_request(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        # Step 3 & 4: Send to AI Module and receive recommendation
        ai_response = analyze_leave(data)

        ai_decision = ai_response.get("decision", "Approve")
        confidence = ai_response.get("confidence", "90%")
        ai_reason = ai_response.get("reason", "Leave processed.")

        # Step 5: Update database record with AI recommendation
        update_ai_recommendation(
            request_id=request_id,
            ai_decision=ai_decision,
            confidence=confidence,
            ai_reason=ai_reason
        )

        # Step 6: Return recommendation to frontend
        return jsonify({
            "decision": ai_decision,
            "confidence": confidence,
            "reason": ai_reason
        }), 200

    except Exception as e:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 4. VIEW LEAVE HISTORY (EMPLOYEE)
# ==========================================
@api_blueprint.route('/history/<employee_id>', methods=['GET'])
def get_history(employee_id):
    """
    GET /history/<employee_id>
    Returns history of leave requests for a given employee.
    """
    try:
        # Check if employee exists
        employee = get_user_by_employee_id(employee_id)
        if not employee:
            return jsonify({"error": "Employee Not Found"}), 404

        history = get_leave_history_by_employee(employee_id)
        return jsonify(history), 200

    except Exception:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 5. VIEW PENDING REQUESTS (MANAGER)
# ==========================================
@api_blueprint.route('/pending', methods=['GET'])
def get_pending():
    """
    GET /pending
    Returns all leave requests with manager_status='Pending'.
    """
    try:
        pending_requests = get_pending_leave_requests()
        return jsonify(pending_requests), 200
    except Exception:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 6. APPROVE LEAVE REQUEST (MANAGER)
# ==========================================
@api_blueprint.route('/approve', methods=['POST'])
def approve_leave():
    """
    POST /approve
    Input: {"id": 1}
    Updates manager_status to 'Approved'.
    """
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"error": "Invalid Input: Missing leave request id"}), 400

        request_id = data.get('id')
        
        # Check if record exists
        leave_req = get_leave_request_by_id(request_id)
        if not leave_req:
            return jsonify({"error": "Leave Request Not Found"}), 404

        success = update_manager_status(request_id, 'Approved')

        if success:
            return jsonify({
                "message": f"Leave Request ID {request_id} has been Approved",
                "id": request_id,
                "status": "Approved"
            }), 200
        else:
            return jsonify({"error": "Failed to update request status"}), 400

    except Exception:
        return jsonify({"error": "Database Error"}), 500


# ==========================================
# 7. REJECT LEAVE REQUEST (MANAGER)
# ==========================================
@api_blueprint.route('/reject', methods=['POST'])
def reject_leave():
    """
    POST /reject
    Input: {"id": 1}
    Updates manager_status to 'Rejected'.
    """
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"error": "Invalid Input: Missing leave request id"}), 400

        request_id = data.get('id')

        # Check if record exists
        leave_req = get_leave_request_by_id(request_id)
        if not leave_req:
            return jsonify({"error": "Leave Request Not Found"}), 404

        success = update_manager_status(request_id, 'Rejected')

        if success:
            return jsonify({
                "message": f"Leave Request ID {request_id} has been Rejected",
                "id": request_id,
                "status": "Rejected"
            }), 200
        else:
            return jsonify({"error": "Failed to update request status"}), 400

    except Exception:
        return jsonify({"error": "Database Error"}), 500
