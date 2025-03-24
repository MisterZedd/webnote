import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-testing'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///webnote.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Webnote specific settings
    DEBUG = int(os.environ.get('DEBUG', '0'))
    HELPEMAIL = os.environ.get('HELPEMAIL') or 'webnote@example.com'
    NUM_DATES = int(os.environ.get('NUM_DATES', '10'))
    TIMEZONE = os.environ.get('TIMEZONE') or 'US/Eastern'