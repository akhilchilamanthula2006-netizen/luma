import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'luma-default-secret-key-change-me')
    
    # MongoDB Config (Ready for when MongoDB is connected)
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/luma_db')
    
    # Groq API Config
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GROQ_MODEL   = os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Mapping of config names
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
