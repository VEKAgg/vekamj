"""Configuration module for bot settings and API keys."""

import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class BotConfig:
    """Bot configuration settings."""
    
    prefix: str = "!"
    description: str = "A modern, feature-rich Discord bot"
    activity_update_interval: int = 120  # seconds
    command_cooldown: int = 3  # seconds
    max_warnings: int = 3
    log_channel_name: str = "bot-logs"
    mod_channel_name: str = "mod-logs"
    welcome_channel_name: str = "welcome"
    default_color: int = 0x7289DA
    error_color: int = 0xFF0000
    success_color: int = 0x00FF00
    info_color: int = 0x3498DB


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    mongodb_uri: str
    redis_uri: str
    mongodb_db_name: str = "vekabot"
    redis_prefix: str = "veka:"
    connection_timeout: int = 5000  # ms


@dataclass
class APIConfig:
    """API keys and configuration."""
    
    discord_token: str
    giphy_key: str
    newsapi_key: str
    rapidapi_key: str
    alphavantage_key: str
    genius_key: str
    github_token: str


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/bot.log"
    max_file_size: int = 5 * 1024 * 1024  # 5 MB
    backup_count: int = 5


@dataclass
class Config:
    """Main configuration class."""
    
    bot: BotConfig
    db: DatabaseConfig
    apis: APIConfig
    logging: LoggingConfig
    
    @classmethod
    def load_from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        # Load .env file if it exists
        env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(env_path)
        
        # Bot Configuration
        bot_config = BotConfig(
            prefix=os.getenv("BOT_PREFIX", "!"),
            description=os.getenv("BOT_DESCRIPTION", "A modern, feature-rich Discord bot")
        )
        
        # Database Configuration
        db_config = DatabaseConfig(
            mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            redis_uri=os.getenv("REDIS_URI", "redis://localhost:6379"),
            mongodb_db_name=os.getenv("MONGODB_DB_NAME", "vekabot")
        )
        
        # API Configuration
        api_config = APIConfig(
            discord_token=os.getenv("DISCORD_TOKEN", ""),
            giphy_key=os.getenv("GIPHY_API_KEY", ""),
            newsapi_key=os.getenv("NEWSAPI_KEY", ""),
            rapidapi_key=os.getenv("RAPIDAPI_KEY", ""),
            alphavantage_key=os.getenv("ALPHAVANTAGE_KEY", ""),
            genius_key=os.getenv("GENIUS_KEY", ""),
            github_token=os.getenv("GITHUB_TOKEN", "")
        )
        
        # Logging Configuration
        logging_config = LoggingConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv(
                "LOG_FORMAT",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            log_file=os.getenv("LOG_FILE", "logs/bot.log")
        )
        
        return cls(
            bot=bot_config,
            db=db_config,
            apis=api_config,
            logging=logging_config
        )


# Create the config instance
config = Config.load_from_env()

# Create example .env file if it doesn't exist
def create_example_env():
    """Create example .env file with all required variables."""
    env_example = """# Bot Configuration
BOT_PREFIX=!
BOT_DESCRIPTION=A modern, feature-rich Discord bot

# Database Configuration
MONGODB_URI=mongodb://localhost:27017
REDIS_URI=redis://localhost:6379
MONGODB_DB_NAME=vekabot

# API Keys
DISCORD_TOKEN=your_discord_token_here
GIPHY_API_KEY=your_giphy_key_here
NEWSAPI_KEY=your_newsapi_key_here
RAPIDAPI_KEY=your_rapidapi_key_here
ALPHAVANTAGE_KEY=your_alphavantage_key_here
GENIUS_KEY=your_genius_key_here
GITHUB_TOKEN=your_github_token_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=logs/bot.log
"""
    
    env_example_path = Path(__file__).parent.parent.parent / ".env.example"
    if not env_example_path.exists():
        with open(env_example_path, "w") as f:
            f.write(env_example)


# Create example .env file when module is imported
create_example_env() 