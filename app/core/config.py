from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BotConfig(BaseModel):
    prefix: str
    description: str
    status: str
    activity: str

class DatabaseConfig(BaseModel):
    class MongoDBConfig(BaseModel):
        uri: str
        database: str

    class RedisConfig(BaseModel):
        uri: str
        prefix: str = "veka:"

    mongodb: MongoDBConfig
    redis: RedisConfig

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str
    file: str

class FeatureConfig(BaseModel):
    music: bool = True
    moderation: bool = True
    economy: bool = True

class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
    logging: LoggingConfig
    features: FeatureConfig

def load_config(config_path: Optional[Path] = None) -> Config:
    """Load and validate configuration from YAML file."""
    if config_path is None:
        config_path = Path("config/config.yaml")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

    return Config(**config_dict)

# Global config instance
config = load_config() 