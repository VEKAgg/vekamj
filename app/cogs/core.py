"""Core commands cog for essential bot functionality."""

import time
from datetime import datetime
from typing import Optional

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.utils.embed_utils import EmbedBuilder


class Core(BaseCog):
    """Core commands for essential bot functionality."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """🏓 Pong! Check the bot's latency."""
        start_time = time.perf_counter()
        message = await ctx.send("Pinging...")
        end_time = time.perf_counter()
        
        duration = round((end_time - start_time) * 1000)
        websocket_latency = round(self.bot.latency * 1000)
        
        embed = EmbedBuilder.default_embed(
            title="🏓 Pong!",
            description="Here are the current latency stats:"
        )
        embed.add_field(
            name="Message Latency",
            value=f"```{duration}ms```",
            inline=True
        )
        embed.add_field(
            name="Websocket Latency",
            value=f"```{websocket_latency}ms```",
            inline=True
        )
        
        await message.edit(content=None, embed=embed)
        
    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Get the bot's invite link."""
        app_info = await self.bot.application_info()
        
        embed = EmbedBuilder.default_embed(
            title="Invite VEKA Bot",
            description="Thanks for your interest in VEKA Bot! Here are the relevant links:"
        )
        
        invite_url = nextcord.utils.oauth_url(
            app_info.id,
            permissions=nextcord.Permissions(
                administrator=True  # You can customize permissions here
            )
        )
        
        embed.add_field(
            name="Bot Invite",
            value=f"[Click here to invite the bot]({invite_url})",
            inline=False
        )
        embed.add_field(
            name="Support Server",
            value="[Join our support server](https://discord.gg/your-invite)",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def info(self, ctx: commands.Context):
        """Get information about the bot."""
        app_info = await self.bot.application_info()
        stats = self.bot.get_bot_stats()
        
        embed = EmbedBuilder.default_embed(
            title="VEKA Bot Information",
            description="A modern, feature-rich Discord bot built with nextcord"
        )
        
        # General Info
        embed.add_field(
            name="Owner",
            value=app_info.owner.mention,
            inline=True
        )
        embed.add_field(
            name="Created",
            value=f"<t:{int(self.bot.user.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Stats
        embed.add_field(
            name="Servers",
            value=f"```{stats['guilds']}```",
            inline=True
        )
        embed.add_field(
            name="Users",
            value=f"```{stats['users']}```",
            inline=True
        )
        embed.add_field(
            name="Commands",
            value=f"```{stats['commands']}```",
            inline=True
        )
        
        # System Info
        embed.add_field(
            name="Python Version",
            value=f"```3.10+```",
            inline=True
        )
        embed.add_field(
            name="Nextcord Version",
            value=f"```{nextcord.__version__}```",
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx: commands.Context, type: str, *, message: str):
        """Set a custom status for the bot (Admin only).
        
        Types: playing, watching, listening, competing
        """
        type_map = {
            "playing": nextcord.ActivityType.playing,
            "watching": nextcord.ActivityType.watching,
            "listening": nextcord.ActivityType.listening,
            "competing": nextcord.ActivityType.competing
        }
        
        if type.lower() not in type_map:
            await ctx.send("Invalid status type. Choose from: playing, watching, listening, competing")
            return
            
        activity_type = type_map[type.lower()]
        self.bot.status_rotator.add_status(activity_type, message)
        
        await ctx.send(f"Added new status: {type} {message}")
        
    @commands.command()
    async def uptime(self, ctx: commands.Context):
        """Check how long the bot has been running."""
        stats = self.bot.get_bot_stats()
        uptime_seconds = stats['uptime']
        
        embed = EmbedBuilder.default_embed(
            title="Bot Uptime",
            description="Here's how long I've been running:"
        )
        
        # Calculate time components
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        # Format uptime string
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} days")
        if hours > 0:
            uptime_parts.append(f"{hours} hours")
        if minutes > 0:
            uptime_parts.append(f"{minutes} minutes")
        if seconds > 0 or not uptime_parts:
            uptime_parts.append(f"{seconds} seconds")
            
        embed.add_field(
            name="Current Uptime",
            value=f"```{', '.join(uptime_parts)}```",
            inline=False
        )
        
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Set up the Core cog."""
    bot.add_cog(Core(bot)) 