import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

class LocalDevelopmentConfig():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLITE_DB_DIR = os.path.join(basedir, '../db_directory')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(SQLITE_DB_DIR, 'database.sqlite3')
    DEBUG = True
    
    # directories
    EXPORT_DIR = os.path.join(basedir, '../static/exports')

    # security
    SECRET_KEY = 'n23049mvqqlmdv09q2adf4'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = "really super secret"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    WTF_CSRF_ENABLED = False
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    REMEMBER_COOKIE_DURATION = timedelta(seconds=900)

    # celery
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

    # webhook
    GCHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAAwDr1jjA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=-ALv_CDyzMMCsSzg4jRh1oAM4GmKaQxe8YkyzfYkjOs%3D"

    # mail
    SMTP_SERVER_HOST = 'localhost'
    SMTP_SERVER_PORT = '1025'
    SENDER_ADDRESS = 'laxminandan@mykanban.com'
    SENDER_PASSWORD = ''
    EMAIL_TEMPLATE = os.path.join(basedir, '../templates/email_template.html')
    REPORT_TEMPLATE = os.path.join(basedir, '../templates/report_template.html')
    REPORTS_DIR = os.path.join(basedir, '../static/monthly_reports')

    # caching
    REDIS_URL = 'redis://localhost:6379'
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379