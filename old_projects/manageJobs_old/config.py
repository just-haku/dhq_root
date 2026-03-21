import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # MongoDB Configuration
    # Simple setup for local MongoDB on Ubuntu
    MONGODB_SETTINGS = {
        'db': os.environ.get('MONGODB_DB') or 'manage_jobs_db',
        'host': os.environ.get('MONGODB_HOST') or 'localhost',
        'port': int(os.environ.get('MONGODB_PORT') or 27017)
    }

    # Upload paths
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'media')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

    # App specific
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}