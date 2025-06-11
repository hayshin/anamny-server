from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    name: str = "Anamny Health Tracker"
    
    # Database
    database_url: str = "postgresql://anamny_user:anamny_password@localhost:5432/anamny_db"
    
    # Authentication
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/Chat
    gemini_api_key: str = ""
    google_api_key: str = ""
    
    # Email (for password reset)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str = "Anamny Health Tracker"


settings = Settings()
