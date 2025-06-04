#!/usr/bin/env python3
"""
Configuration settings for CyberGuard AI Flask Application
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cyberguard-ai-super-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'data/threats.db'
    
    # API configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100/hour'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:3001',
        'http://127.0.0.1:3001'
    ]
    
    # WebSocket configuration
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # Real-time service configuration
    REALTIME_MAX_THREAT_HISTORY = 1000
    REALTIME_MAX_METRICS_HISTORY = 100
    REALTIME_USER_TIMEOUT_SECONDS = 300  # 5 minutes
    REALTIME_METRICS_UPDATE_INTERVAL = 5  # seconds
    REALTIME_USER_ACTIVITY_CHECK_INTERVAL = 30  # seconds
    
    # AI Model configuration
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'model/threat_detector_model.h5'
    MODEL_SCALER_PATH = os.environ.get('MODEL_SCALER_PATH') or 'model/scaler.pkl'
    MODEL_THREAT_THRESHOLD = float(os.environ.get('MODEL_THREAT_THRESHOLD', '0.5'))
    MODEL_MAX_INPUT_LENGTH = int(os.environ.get('MODEL_MAX_INPUT_LENGTH', '1000'))
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_DIR = os.environ.get('LOG_DIR') or 'logs'
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
    
    # Security configuration
    SESSION_TIMEOUT = timedelta(hours=24)
    BCRYPT_LOG_ROUNDS = 12
    
    # Threat detection configuration
    THREAT_LEVELS = ['low', 'medium', 'high', 'critical']
    DEFAULT_THREAT_LEVEL = 'medium'
    
    # Performance configuration
    MAX_CONCURRENT_CONNECTIONS = int(os.environ.get('MAX_CONCURRENT_CONNECTIONS', '100'))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Shorter timeouts for faster development
    SOCKETIO_PING_TIMEOUT = 30
    REALTIME_USER_TIMEOUT_SECONDS = 120  # 2 minutes


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # More restrictive CORS in production
    CORS_ORIGINS = [
        'https://your-domain.com',
        'https://www.your-domain.com'
    ]
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Longer timeouts for production stability
    SOCKETIO_PING_TIMEOUT = 60
    REALTIME_USER_TIMEOUT_SECONDS = 600  # 10 minutes
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/cyberguard.log',
                maxBytes=Config.LOG_MAX_BYTES,
                backupCount=Config.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('CyberGuard AI startup')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    DATABASE_PATH = ':memory:'
    
    # Disable rate limiting for tests
    API_RATE_LIMIT = None
    
    # Fast timeouts for testing
    SOCKETIO_PING_TIMEOUT = 5
    REALTIME_USER_TIMEOUT_SECONDS = 10


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 