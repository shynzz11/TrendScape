import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/users.db')  # Default to SQLite for local development

# Secret key for session management
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Cloud storage configuration (for badge storage)
CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET', '')
CLOUD_STORAGE_KEY = os.getenv('CLOUD_STORAGE_KEY', '')
CLOUD_STORAGE_SECRET = os.getenv('CLOUD_STORAGE_SECRET', '')