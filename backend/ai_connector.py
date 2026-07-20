"""
ai_connector.py
===============
AI Connector module for evaluating employee leave requests.
Currently returns mock recommendations. Can be updated later to integrate with external LLM APIs (e.g. OpenAI).
"""

def analyze_leave(data):
    """
    Analyzes a leave request dictionary and returns an AI decision recommendation.

    Input Data Structure:
    {
        "employee_id": "EMP101",
        "leave_type": "Medical",
        "start_date": "2026-07-20",
        "end_date": "2026-07-22",
        "reason": "High Fever"
    }

    Returns:
    {
        "decision": "Approve" | "Reject",
        "confidence": "95%",
        "reason": "Explanation summary"
    }
    """
    leave_type = data.get("leave_type", "").strip()
    reason = data.get("reason", "").strip()

    # Smart mock recommendation rule logic based on leave type / reasoning
    if "Medical" in leave_type or "fever" in reason.lower() or "hospital" in reason.lower():
        return {
            "decision": "Approve",
            "confidence": "95%",
            "reason": "Medical leave with valid justification."
        }
    elif "Casual" in leave_type or "vacation" in reason.lower() or "personal" in reason.lower():
        return {
            "decision": "Approve",
            "confidence": "88%",
            "reason": "Casual leave request within acceptable department threshold."
        }
    else:
        # Default mock fallback response as requested in prompt specification
        return {
            "decision": "Approve",
            "confidence": "94%",
            "reason": "Leave request appears valid based on submitted details."
        }
