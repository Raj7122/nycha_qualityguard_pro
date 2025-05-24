"""
NYCHA QualityGuard Pro Backend Application
Main application entry point for the NYCHA QualityGuard Pro backend service.
"""

import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from backend.api.routes.data_routes import data_bp
from backend.api.routes.complaints_routes import complaints_bp
from backend.api.routes.maintenance_routes import maintenance_bp
from backend.api.routes.agents_routes import agents_bp
from backend.config import DevelopmentConfig

# Load environment variables from .env file
load_dotenv()

def create_app(config_object=DevelopmentConfig):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_object)
    
    # Register blueprints
    app.register_blueprint(data_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(agents_bp)
    
    # Register routes
    @app.route('/')
    def root():
        """Root endpoint that returns the application status."""
        return jsonify({
            "status": "NYCHA QualityGuard Pro Backend Running",
            "version": "1.0.0"
        })

    @app.route('/api/test')
    def test_api():
        """Test endpoint to verify API functionality."""
        return jsonify({
            "message": "API is working!",
            "status": "success"
        })
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    host = app.config.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    
    app.run(
        host=host,
        port=port,
        debug=debug
    ) 