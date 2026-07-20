import os

# ==========================================
# CONFIGURATION SETTINGS
# ==========================================

# Base directory of the backend folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory and file path for SQLite database
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'leave_system.db')

# Secret key for Flask application session/security
SECRET_KEY = 'hackathon-secret-key-leave-system'

# Debug mode flag for Flask development server
DEBUG = True
