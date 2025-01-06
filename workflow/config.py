import os

class Config:
    SECRET_KEY = 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///workflow.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    DEBUG = True

# Database Configuration
DB_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'workflow_db',
    }
}

# Application Configuration
SECRET_KEY = 'your-secret-key-here'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
