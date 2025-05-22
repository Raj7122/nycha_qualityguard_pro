"""
Development configuration for NYCHA QualityGuard Pro.
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
    PORT = 5002  # Changed to 5002 to avoid conflicts
    
    # Environment
    ENV = 'development'
    
    # API settings
    NYC_OPENDATA_APP_TOKEN = 'your_app_token_here'
    
    # Database settings
    DATABASE_URL = 'postgresql://user:password@localhost:5432/nychaguard'
    
    # OpenAI settings
    OPENAI_API_KEY = 'your_openai_api_key_here'
    
    # Backend API settings
    BACKEND_API_URL = 'http://localhost:5002' 