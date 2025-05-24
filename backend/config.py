"""
Configuration settings for NYCHA QualityGuard Pro
"""

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    PORT = 5000
    HOST = '0.0.0.0'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False 