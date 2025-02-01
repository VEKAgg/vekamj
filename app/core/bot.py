"""Core bot module."""

from pathlib import Path
from typing import Optional, Dict, Any

import nextcord
from nextcord.ext import commands

from app.core.config import config
from app.core.logger import logger
from app.database.mongodb import db
from app.database.redis import redis
from app.utils.status_rotator import StatusRotator


class VekaBot(commands.Bot):
    """Main bot class with extended functionality."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.bot.prefix),
            description=config.bot.description,
            intents=intents,
            case_insensitive=True,
            strip_after_prefix=True,
        )
        
        self.logger = logger
        self.status_rotator: Optional[StatusRotator] = None
        self.command_stats: Dict[str, int] = {}
        
    async def setup_hook(self) -> None:
        """Setup hook that runs before the bot starts."""
        # Initialize databases
        await self._init_databases()
        
        # Initialize status rotator
        self.status_rotator = StatusRotator(self)
        
        # Load cogs
        await self.load_extensions()
        
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
        
    async def on_command(self, ctx: commands.Context):
        """Event triggered when a command is about to be invoked."""
        # Update command stats
        self.command_stats[ctx.command.qualified_name] = (
            self.command_stats.get(ctx.command.qualified_name, 0) + 1
        )
        
        # Log command usage
        self.logger.info(
            f"Command '{ctx.command.qualified_name}' used by {ctx.author} (ID: {ctx.author.id}) "
            f"in guild {ctx.guild.name} (ID: {ctx.guild.id})"
        )
        
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
            
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds."
            )
            return
            
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
            return
            
        # Log unexpected errors
        self.logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
        await ctx.send(
            "An unexpected error occurred. Please try again later. "
            "If the problem persists, contact the bot administrators."
        )
        
    async def get_command_stats(self) -> Dict[str, Any]:
        """Get command usage statistics."""
        total_commands = sum(self.command_stats.values())
        return {
            "total_commands": total_commands,
            "command_counts": dict(sorted(
                self.command_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )),
            "most_used": max(self.command_stats.items(), key=lambda x: x[1]) if self.command_stats else None
        }
        
    def get_bot_stats(self) -> Dict[str, Any]:
        """Get general bot statistics."""
        return {
            "guilds": len(self.guilds),
            "users": sum(g.member_count for g in self.guilds),
            "channels": sum(len(g.channels) for g in self.guilds),
            "commands": len(self.commands),
            "cogs": len(self.cogs),
            "uptime": self.uptime.total_seconds() if hasattr(self, 'uptime') else 0
        } 