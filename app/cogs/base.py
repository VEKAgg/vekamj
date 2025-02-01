from typing import Optional

from nextcord.ext import commands

from app.core.logger import logger

class BaseCog(commands.Cog):
    """Base cog that all other cogs should inherit from."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logger.getChild(self.__class__.__name__)
        
    async def cog_load(self) -> None:
        """Called when the cog is loaded."""
        self.logger.info(f"{self.__class__.__name__} cog loaded")
        
    async def cog_unload(self) -> None:
        """Called when the cog is unloaded."""
        self.logger.info(f"{self.__class__.__name__} cog unloaded")
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        """Global check for all commands in this cog."""
        return True
        
    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Local error handler for this cog."""
        self.logger.error(f"Error in {ctx.command}: {error}", exc_info=error)
        
    @staticmethod
    def format_help(command: commands.Command) -> str:
        """Format help message for a command."""
        return (
            f"```\n"
            f"Usage: {command.qualified_name} {command.signature}\n"
            f"{command.help or 'No help available.'}\n"
            f"```"
        ) 