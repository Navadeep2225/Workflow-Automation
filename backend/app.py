"""
app.py
======
Main entry point for the AI-Powered Leave Approval System Backend.
Initializes Flask, configures CORS, automatically sets up the SQLite database,
and registers API routes.
"""

from flask import Flask
from flask_cors import CORS
import config
from database import init_db
from routes import api_blueprint

def create_app():
    """
    Application Factory function to construct and configure the Flask app.
    """
    app = Flask(__name__)
    
    # Load configuration settings from config.py
    app.config.from_object(config)

    # Enable Cross-Origin Resource Sharing (CORS) so frontend applications can communicate with APIs
    CORS(app)

    # Automatically create database directory, database file, and required tables if they don't exist
    init_db()

    # Register API blueprint containing all route handlers
    app.register_blueprint(api_blueprint)

    return app

# Initialize the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run development server on port 5000
    print("[INFO] Starting AI Leave Approval System Backend...")
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
