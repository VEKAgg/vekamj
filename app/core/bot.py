"""Core bot module."""

from pathlib import Path
from typing import Optional

import nextcord
from nextcord.ext import commands

from app.core.config import config
from app.core.logger import logger
from app.database.mongodb import db
from app.database.redis import redis


class VekaBot(commands.Bot):
    """Main bot class with extended functionality."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.bot.prefix),
            description=config.bot.description,
            intents=intents,
        )
        
        self.logger = logger
        
    async def setup_hook(self) -> None:
        """Setup hook that runs before the bot starts."""
        # Initialize databases
        await self._init_databases()
        
        # Load cogs
        await self.load_extensions()
        
        # Set activity
        activity = nextcord.Activity(
            type=nextcord.ActivityType.playing,
            name=config.bot.activity
        )
        await self.change_presence(status=nextcord.Status.online, activity=activity)
        
    async def _init_databases(self) -> None:
        """Initialize database connections."""
        try:
            # Connect to MongoDB
            await db.connect()
            self.logger.info("MongoDB connection established")
            
            # Connect to Redis
            await redis.connect()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.error(f"Failed to initialize databases: {e}")
            raise
            
    async def close(self) -> None:
        """Clean up bot resources."""
        # Close database connections
        try:
            await db.close()
            await redis.close()
        except Exception as e:
            self.logger.error(f"Error closing database connections: {e}")
            
        await super().close()
        
    async def load_extensions(self, cogs_dir: Optional[Path] = None) -> None:
        """Load all cogs from the specified directory."""
        if cogs_dir is None:
            cogs_dir = Path(__file__).parent.parent / "cogs"
            
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
                
            extension_path = f"app.cogs.{cog_file.stem}"
            try:
                await self.load_extension(extension_path)
                self.logger.info(f"Loaded extension: {extension_path}")
            except Exception as e:
                self.logger.error(f"Failed to load extension {extension_path}: {e}")
                
    async def on_ready(self):
        """Event triggered when the bot is ready."""
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.logger.info(f"Connected to {len(self.guilds)} guilds")
        
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
            
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
            return
            
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
            return
            
        # Log unexpected errors
        self.logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
        await ctx.send("An unexpected error occurred. Please try again later.") 