"""Utility commands for general server and user management."""

import pytz
from datetime import datetime
from typing import Optional

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.utils.embed_utils import EmbedBuilder
from app.database.redis_manager import redis


class Utility(BaseCog):
    """Utility commands for server management and user tools."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        
    @commands.command()
    async def time(self, ctx: commands.Context, timezone: str = "UTC"):
        """Get current time for a specific timezone.
        
        Example: !time US/Pacific
        """
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            
            embed = EmbedBuilder.default_embed(
                title=f"Time in {timezone}",
                description=f"🕒 {current_time.strftime('%I:%M %p, %A %B %d, %Y')}"
            )
            await ctx.send(embed=embed)
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send(f"Unknown timezone: {timezone}. Try using a valid timezone like 'US/Pacific' or 'Europe/London'.")
            
    @commands.command()
    async def channelinfo(self, ctx: commands.Context):
        """Display information about the current channel."""
        channel = ctx.channel
        
        embed = EmbedBuilder.default_embed(
            title=f"#{channel.name} Information",
            description=channel.topic or "No topic set"
        )
        
        # Basic Info
        embed.add_field(
            name="Channel ID",
            value=f"```{channel.id}```",
            inline=True
        )
        embed.add_field(
            name="Category",
            value=f"```{channel.category.name if channel.category else 'None'}```",
            inline=True
        )
        
        # Channel Type & Settings
        embed.add_field(
            name="Type",
            value=f"```{str(channel.type).title()}```",
            inline=True
        )
        if isinstance(channel, nextcord.TextChannel):
            embed.add_field(
                name="Slowmode",
                value=f"```{channel.slowmode_delay}s```" if channel.slowmode_delay else "```Disabled```",
                inline=True
            )
            embed.add_field(
                name="NSFW",
                value=f"```{'Yes' if channel.is_nsfw() else 'No'}```",
                inline=True
            )
            
        # Permissions
        embed.add_field(
            name="Created At",
            value=f"<t:{int(channel.created_at.timestamp())}:R>",
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def emojiinfo(self, ctx: commands.Context, emoji: nextcord.Emoji):
        """Show details about a server emoji.
        
        Example: !emojiinfo 😀
        """
        embed = EmbedBuilder.default_embed(
            title=f"Emoji Information: {emoji.name}",
            description=f"ID: {emoji.id}"
        )
        
        embed.set_thumbnail(url=emoji.url)
        
        embed.add_field(
            name="Created At",
            value=f"<t:{int(emoji.created_at.timestamp())}:R>",
            inline=True
        )
        embed.add_field(
            name="Animated",
            value=f"```{'Yes' if emoji.animated else 'No'}```",
            inline=True
        )
        embed.add_field(
            name="Available",
            value=f"```{'Yes' if emoji.available else 'No'}```",
            inline=True
        )
        embed.add_field(
            name="URL",
            value=f"[Click Here]({emoji.url})",
            inline=True
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def afk(self, ctx: commands.Context, *, message: str = "AFK"):
        """Set yourself as AFK with an optional message.
        
        Example: !afk Be back in 10 minutes
        """
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        
        # Store AFK status in Redis with 24-hour expiry
        await redis.set(
            f"afk:{guild_id}:{user_id}",
            message,
            expire=86400  # 24 hours
        )
        
        # Update nickname if possible
        try:
            if ctx.author.guild_permissions.change_nickname:
                await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
        except Exception:
            pass
            
        await ctx.send(f"{ctx.author.mention} I've set your AFK status: {message}")
        
    @commands.command()
    async def nick(self, ctx: commands.Context, *, nickname: str = None):
        """Change your nickname (if permissions allow).
        
        Example: !nick Cool Guy
        """
        try:
            await ctx.author.edit(nick=nickname)
            if nickname:
                await ctx.send(f"Changed your nickname to: {nickname}")
            else:
                await ctx.send("Reset your nickname to your username.")
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to change your nickname!")
        except Exception as e:
            await ctx.send(f"Failed to change nickname: {str(e)}")
            
    @commands.command()
    async def serverbanner(self, ctx: commands.Context):
        """Show the server's banner."""
        if not ctx.guild.banner:
            await ctx.send("This server doesn't have a banner!")
            return
            
        embed = EmbedBuilder.default_embed(
            title=f"{ctx.guild.name}'s Banner"
        )
        embed.set_image(url=ctx.guild.banner.url)
        await ctx.send(embed=embed)
        
    @commands.command()
    async def banner(self, ctx: commands.Context, user: nextcord.Member = None):
        """Display a user's banner.
        
        Example: !banner @user
        """
        user = user or ctx.author
        user = await self.bot.fetch_user(user.id)
        
        if not user.banner:
            await ctx.send(f"{user.name} doesn't have a banner!")
            return
            
        embed = EmbedBuilder.default_embed(
            title=f"{user.name}'s Banner"
        )
        embed.set_image(url=user.banner.url)
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 minutes cooldown
    async def report(self, ctx: commands.Context, user: nextcord.Member, *, reason: str):
        """Report a user to server admins.
        
        Example: !report @user Inappropriate behavior
        """
        # Delete the report message to keep it private
        await ctx.message.delete()
        
        # Create report embed
        embed = EmbedBuilder.default_embed(
            title="⚠️ User Report",
            description=f"A report has been filed against {user.mention}"
        )
        
        embed.add_field(
            name="Reported By",
            value=ctx.author.mention,
            inline=True
        )
        embed.add_field(
            name="Channel",
            value=ctx.channel.mention,
            inline=True
        )
        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )
        
        # Try to send to moderation channel, fall back to first channel with mod permissions
        mod_channel = None
        for channel in ctx.guild.channels:
            if isinstance(channel, nextcord.TextChannel):
                if "mod" in channel.name.lower() or "admin" in channel.name.lower():
                    mod_channel = channel
                    break
                    
        if mod_channel:
            await mod_channel.send(embed=embed)
            await ctx.author.send("Your report has been submitted to the moderators.")
        else:
            await ctx.author.send("Could not find a moderation channel. Please contact a server admin directly.")
            
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.channel)
    async def poll(self, ctx: commands.Context, *, content: str):
        """Create a poll with multiple options.
        
        Example: !poll What's your favorite color? | Red | Blue | Green
        """
        # Split content into question and options
        parts = [p.strip() for p in content.split("|")]
        if len(parts) < 3:
            await ctx.send("Please provide a question and at least 2 options separated by |")
            return
            
        question = parts[0]
        options = parts[1:]
        
        if len(options) > 10:
            await ctx.send("Maximum 10 options allowed!")
            return
            
        # Create poll embed
        embed = EmbedBuilder.default_embed(
            title="📊 " + question,
            description="\n\n".join(f"{chr(127462 + i)} {option}" for i, option in enumerate(options))
        )
        
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")
        
        # Send poll and add reactions
        poll_message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await poll_message.add_reaction(chr(127462 + i))


def setup(bot: commands.Bot) -> None:
    """Set up the Utility cog."""
    bot.add_cog(Utility(bot)) 