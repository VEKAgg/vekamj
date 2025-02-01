"""Core bot class."""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp
import nextcord
from nextcord.ext import commands

from app.utils.status_rotator import StatusRotator
from app.database.mongodb import MongoDB
from app.database.redis_manager import RedisManager
from app.core.config import config
from app.core.logger import logger


class VekaBot(commands.Bot):
    """Main bot class for VEKA."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        
        super().__init__(
            command_prefix=config.bot.prefix,
            intents=intents,
            help_command=None  # We'll implement our own help command
        )
        
        # Initialize components
        self.start_time = time.time()
        self.command_usage: Dict[str, int] = {}
        self.status_rotator: Optional[StatusRotator] = None
        self.db: Optional[MongoDB] = None
        self.redis: Optional[RedisManager] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Set up logging
        self.logger = logger
        
    async def setup_hook(self) -> None:
        """Initialize bot components after login."""
        try:
            # Initialize aiohttp session
            self.session = aiohttp.ClientSession()
            
            # Initialize databases
            self.db = MongoDB()
            await self.db.connect()
            
            self.redis = RedisManager()
            await self.redis.connect()
            
            # Initialize status rotator
            self.status_rotator = StatusRotator(self)
            await self.status_rotator.start()
            
            # Load cogs
            await self.load_extensions()
            
            self.logger.info("Bot setup complete!")
        except Exception as e:
            self.logger.error(f"Error during setup: {e}")
            await self.close()
            raise
            
    async def load_extensions(self) -> None:
        """Load all cog extensions."""
        cogs_dir = Path(__file__).parent / "cogs"
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.stem == "base":
                continue
                
            try:
                await self.load_extension(f"app.cogs.{cog_file.stem}")
                self.logger.info(f"Loaded extension: {cog_file.stem}")
            except Exception as e:
                self.logger.error(f"Failed to load extension {cog_file.stem}: {e}")
                
    async def on_ready(self):
        """Event triggered when the bot is ready."""
        self.logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.logger.info(f"Connected to {len(self.guilds)} guilds")
                
    async def on_command(self, ctx: commands.Context) -> None:
        """Log command usage."""
        command_name = ctx.command.qualified_name
        self.command_usage[command_name] = self.command_usage.get(command_name, 0) + 1
        
        # Log to database if available
        if self.db:
            await self.db.log_event(
                "command_used",
                {
                    "command": command_name,
                    "user_id": str(ctx.author.id),
                    "guild_id": str(ctx.guild.id) if ctx.guild else None,
                    "channel_id": str(ctx.channel.id)
                }
            )
            
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds."
            )
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send("This command can only be used in private messages.")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        else:
            # Log unexpected errors
            self.logger.error(f"Command error in {ctx.command}: {error}")
            await ctx.send("An error occurred while processing your command.")
            
    def get_bot_stats(self) -> Dict[str, int]:
        """Get current bot statistics."""
        return {
            "guilds": len(self.guilds),
            "users": sum(g.member_count for g in self.guilds),
            "commands": len(self.commands),
            "command_uses": sum(self.command_usage.values()),
            "uptime": int(time.time() - self.start_time)
        }
        
    async def close(self) -> None:
        """Clean up resources before shutdown."""
        try:
            # Stop status rotator
            if self.status_rotator:
                self.status_rotator.stop()
            
            # Close database connections
            if self.db:
                await self.db.close()
            
            if self.redis:
                await self.redis.close()
                
            # Close aiohttp session
            if self.session:
                await self.session.close()
                
            # Call parent close
            await super().close()
            
            self.logger.info("Bot shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise 