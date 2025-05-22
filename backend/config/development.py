"""
Development configuration for the NYCHA QualityGuard Pro Backend.
"""

class DevelopmentConfig:
    """Development configuration settings."""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # API settings
    JSON_SORT_KEYS = False
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Environment
    ENV = 'development' 