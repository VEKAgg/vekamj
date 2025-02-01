"""Activity tracking cog for monitoring user activities."""

from typing import Dict, Optional, Set

import nextcord
from nextcord import Member
from nextcord.ext import commands, tasks

from app.cogs.base import BaseCog
from app.database.mongodb import db
from app.utils.embed_utils import EmbedBuilder


class Activity(BaseCog):
    """Activity tracking module for monitoring user activities."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.activity_cache: Dict[int, Dict[int, Set[str]]] = {}
        self.clean_cache.start()
        
    def cog_unload(self) -> None:
        """Clean up when cog is unloaded."""
        self.clean_cache.cancel()
        
    @tasks.loop(hours=1)
    async def clean_cache(self) -> None:
        """Clean up activity cache periodically."""
        self.activity_cache.clear()
        self.logger.info("Cleaned activity cache")
        
    async def _should_track_activity(self, before: Optional[nextcord.Activity],
                                   after: Optional[nextcord.Activity]) -> bool:
        """Determine if activity change should be tracked."""
        if not after:
            return False
            
        # Skip if same activity
        if before and before.name == after.name and before.type == after.type:
            return False
            
        # Initialize cache for guild and user if needed
        guild_id = after.guild_id if hasattr(after, 'guild_id') else 0
        user_id = after.user.id if hasattr(after, 'user') else 0
        
        if guild_id not in self.activity_cache:
            self.activity_cache[guild_id] = {}
        if user_id not in self.activity_cache[guild_id]:
            self.activity_cache[guild_id][user_id] = set()
            
        # Check if activity was recently tracked
        activity_key = f"{after.type}:{after.name}"
        if activity_key in self.activity_cache[guild_id][user_id]:
            return False
            
        # Add to cache
        self.activity_cache[guild_id][user_id].add(activity_key)
        return True
        
    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        """Handle member activity updates."""
        try:
            # Get activity changes
            before_activity = next((a for a in before.activities if a.type != nextcord.ActivityType.custom), None)
            after_activity = next((a for a in after.activities if a.type != nextcord.ActivityType.custom), None)
            
            if not await self._should_track_activity(before_activity, after_activity):
                return
                
            # Track activity
            if after_activity:
                activity_data = {
                    "type": after_activity.type.name,
                    "name": after_activity.name,
                    "details": getattr(after_activity, "details", None),
                    "url": getattr(after_activity, "url", None)
                }
                
                # Update database
                await db.update_user_activity(after.id, after.guild.id, activity_data)
                
                # Log event
                await db.log_event(
                    "activity_update",
                    after.guild.id,
                    {
                        "user_id": after.id,
                        "activity": activity_data
                    }
                )
                
                # Send activity update if configured
                if after_activity.type in {
                    nextcord.ActivityType.streaming,
                    nextcord.ActivityType.playing,
                    nextcord.ActivityType.competing
                }:
                    # Get announcement channel (you might want to make this configurable)
                    channel = after.guild.system_channel
                    if channel and channel.permissions_for(after.guild.me).send_messages:
                        embed = EmbedBuilder.activity_embed(after, after_activity)
                        await channel.send(embed=embed)
                        
        except Exception as e:
            self.logger.error(f"Error tracking activity for {after.id}: {e}")
            
    @commands.command()
    async def activity(self, ctx: commands.Context, member: Optional[Member] = None) -> None:
        """Show recent activity for a user."""
        try:
            target = member or ctx.author
            events = await db.get_recent_events(
                ctx.guild.id,
                event_type="activity_update",
                limit=5
            )
            
            if not events:
                await ctx.send(embed=EmbedBuilder.info_embed(
                    "Activity History",
                    f"No recent activity found for {target.display_name}"
                ))
                return
                
            # Create activity embed
            embed = EmbedBuilder.default_embed(
                f"Recent Activity - {target.display_name}",
                "Most recent activities:"
            )
            
            for event in events:
                activity = event["data"]["activity"]
                embed.add_field(
                    name=f"{activity['type'].title()} - {activity['name']}",
                    value=f"Started: <t:{int(event['timestamp'].timestamp())}:R>\n"
                          f"Details: {activity['details'] or 'N/A'}",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error showing activity history: {e}")
            await ctx.send(embed=EmbedBuilder.error_embed("Failed to fetch activity history."))


def setup(bot: commands.Bot) -> None:
    """Set up the Activity cog."""
    bot.add_cog(Activity(bot)) 