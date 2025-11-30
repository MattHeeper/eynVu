import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """
    Main configuration class for eynVu bot
    All settings loaded from .env file
    """
    
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "eynme")
    DB_USER = os.getenv("DB_USER", "eynme_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    
    # Database URL for SQLAlchemy
    DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Channel Configuration (optional)
    CHANNEL_ID = os.getenv("CHANNEL_ID")
    
    # Bot Settings
    BOT_NAME = "eynVu"
    BOT_VERSION = "1.0.0"
    
    # Features Toggle
    ENABLE_LOGGING = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Limits
    MAX_NICKNAME_LENGTH = 13
    MAX_PLAYLIST_SONGS = 9
    GALLERY_SLIDE_INTERVAL = 900  # 15 minutes in seconds
    
    # Identifier Format
    IDENTIFIER_PREFIX = "Ua"  # User anonymous
    STATION_PREFIX = "Rs"     # Radio station
    
    @classmethod
    def validate(cls):
        """
        Validate required configuration
        Raises ValueError if critical settings are missing
        """
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required in .env file")
        
        if not cls.ADMIN_ID:
            raise ValueError("ADMIN_ID is required in .env file")
        
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD is required in .env file")
        
        return True
    
    @classmethod
    def get_info(cls):
        """
        Return bot information as dictionary
        """
        return {
            "name": cls.BOT_NAME,
            "version": cls.BOT_VERSION,
            "database": cls.DB_NAME,
            "admin_id": cls.ADMIN_ID
        }


# Validate config on import
try:
    Config.validate()
    print(f"✅ Configuration loaded successfully!")
    print(f"📊 Bot: {Config.BOT_NAME} v{Config.BOT_VERSION}")
    print(f"💾 Database: {Config.DB_NAME}")
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    exit(1)
