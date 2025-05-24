"""
Run script for NYCHA QualityGuard Pro Backend
Sets up the Python path and runs the Flask application.
"""

import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app import app

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    host = app.config.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    
    app.run(
        host=host,
        port=port,
        debug=debug
    ) 