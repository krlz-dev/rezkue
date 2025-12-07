"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from config import config


def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Register blueprints
    from app.controllers.main import main_bp
    from app.controllers.video import video_bp
    from app.controllers.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
