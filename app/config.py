import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///ims.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")