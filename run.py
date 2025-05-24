"""
Run script for NYCHA QualityGuard Pro Backend
"""

import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 