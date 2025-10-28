from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # MongoDB
    MONGO_URL: str = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME: str = os.getenv('DB_NAME', 'seo_platform')
    
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION: int = 86400  # 24 hours
    
    # AI LLM
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL: str = 'llama-3.3-70b-versatile'
    EMERGENT_LLM_KEY: str = os.getenv('EMERGENT_LLM_KEY', '')
    
    # PayPal
    PAYPAL_CLIENT_ID: str = os.getenv('PAYPAL_CLIENT_ID', '')
    PAYPAL_CLIENT_SECRET: str = os.getenv('PAYPAL_CLIENT_SECRET', '')
    PAYPAL_MODE: str = os.getenv('PAYPAL_MODE', 'sandbox')  # sandbox or live
    
    # Credits
    FREE_SIGNUP_CREDITS: int = 20
    
    # CORS
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    
    # Super Admin
    SUPER_ADMIN_EMAIL: str = os.getenv('SUPER_ADMIN_EMAIL', 'admin@rankforge.com')
    SUPER_ADMIN_PASSWORD: str = os.getenv('SUPER_ADMIN_PASSWORD', 'RankForge@Admin2025!Secure')
    
    # Competitor Analysis APIs
    EXA_API_KEY: str = os.getenv('EXA_API_KEY', '')
    
    # Reddit API
    REDDIT_CLIENT_ID: str = os.getenv('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET: str = os.getenv('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT: str = os.getenv('REDDIT_USER_AGENT', 'RankForge SEO Platform v1.0')
    
    # Twitter/X API
    TWITTER_CLIENT_ID: str = os.getenv('TWITTER_CLIENT_ID', '')
    TWITTER_CLIENT_SECRET: str = os.getenv('TWITTER_CLIENT_SECRET', '')
    
    class Config:
        env_file = '.env'

@lru_cache()
def get_settings() -> Settings:
    return Settings()
