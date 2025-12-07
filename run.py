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
    print("=" * 60)
    print("HDRezka MVC Application")
    print("=" * 60)
    print("Starting server on http://localhost:5001")
    print("\nEndpoints:")
    print("  GET  /              - Home page with search")
    print("  GET  /search?q=...  - Search for videos")
    print("  GET  /watch?url=... - Video player")
    print("  POST /api/episodes  - Get episodes for series")
    print("  POST /api/season_episodes - Get season episodes")
    print("  POST /api/stream    - Get stream URLs")
    print("  GET  /health        - Health check")
    print("=" * 60)
    print("\n✨ Using HdRezkaApi library for reliable access!")
    print("   - No more anti-bot blocking")
    print("   - Proper stream URL decoding")
    print("   - Season/episode switching works!")
    print("   - MVC architecture with Jinja2 templates")
    print("=" * 60)
    print()

    # Run the application
    app.run(debug=True, port=5001, host='0.0.0.0')
