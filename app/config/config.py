import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-hard-to-guess-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for cPanel
    EMAIL_SETTINGS = {
        'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'mail.yourdomain.com'),
        'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
        'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1'],
        'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', 'noreply@yourdomain.com'),
        'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', ''),
        'MAIL_SENDER_NAME': os.environ.get('MAIL_SENDER_NAME', 'LinkedIn CRM'),
        'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
    }
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:password@localhost/linkedin_crm'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/linkedin_crm'
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 