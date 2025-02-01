"""Status rotator for dynamic bot presence."""

import asyncio
from typing import List, Optional

import nextcord
from nextcord.ext import tasks

from app.core.logger import logger


class StatusRotator:
    """Manages rotating bot status messages."""
    
    def __init__(self, bot):
        """Initialize the status rotator."""
        self.bot = bot
        self.current_index = 0
        self.statuses: List[dict] = [
            {
                "type": nextcord.ActivityType.watching,
                "name": "{guild_count} servers"
            },
            {
                "type": nextcord.ActivityType.listening,
                "name": "{user_count} users"
            },
            {
                "type": nextcord.ActivityType.playing,
                "name": "v help for commands"
            },
            {
                "type": nextcord.ActivityType.competing,
                "name": "the leaderboard"
            }
        ]
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the status rotation."""
        if not self._task:
            self.rotate_status.start()
            self._task = asyncio.create_task(self._rotation_loop())
            logger.info("Status rotator started")
            
    def stop(self):
        """Stop the status rotation."""
        if self._task:
            self.rotate_status.cancel()
            self._task.cancel()
            self._task = None
            logger.info("Status rotator stopped")
            
    def _format_status(self, status: dict) -> dict:
        """Format status with current bot stats."""
        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count for g in self.bot.guilds)
        
        return {
            "type": status["type"],
            "name": status["name"].format(
                guild_count=guild_count,
                user_count=user_count
            )
        }
        
    @tasks.loop(minutes=2)
    async def rotate_status(self):
        """Rotate through status messages."""
        try:
            status = self._format_status(self.statuses[self.current_index])
            
            activity = nextcord.Activity(
                type=status["type"],
                name=status["name"]
            )
            await self.bot.change_presence(activity=activity)
            
            self.current_index = (self.current_index + 1) % len(self.statuses)
        except Exception as e:
            logger.error(f"Error rotating status: {e}")
            
    @rotate_status.before_loop
    async def before_rotate_status(self):
        """Wait for bot to be ready before starting rotation."""
        await self.bot.wait_until_ready()
        
    async def _rotation_loop(self):
        """Background task for status rotation."""
        try:
            while True:
                await asyncio.sleep(120)  # 2 minutes
                await self.rotate_status()
        except asyncio.CancelledError:
            logger.info("Status rotation loop cancelled")
        except Exception as e:
            logger.error(f"Error in status rotation loop: {e}")
            
    def add_status(self, type: nextcord.ActivityType, name: str):
        """Add a new status to the rotation."""
        self.statuses.append({
            "type": type,
            "name": name
        })
        
    def remove_status(self, index: int) -> Optional[dict]:
        """Remove a status from the rotation."""
        if 0 <= index < len(self.statuses):
            return self.statuses.pop(index)
        return None 