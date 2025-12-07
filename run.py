#!/usr/bin/env python3
"""
HDRezka MVC Application - Entry Point
Run this file to start the web application
"""
from app import create_app
import os

# Create the Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Get debug mode from environment variable (default: False for production)
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'

    # Run the application
    app.run(debug=debug_mode, port=5001, host='0.0.0.0')
