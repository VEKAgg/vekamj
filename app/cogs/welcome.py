"""Welcome cog for handling member joins and invite tracking."""

from typing import Dict, Optional

import nextcord
from nextcord import Invite, Member
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.database.mongodb import db
from app.utils.embed_utils import EmbedBuilder


class Welcome(BaseCog):
    """Welcome module for handling new members and invite tracking."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.invites: Dict[int, Dict[str, Invite]] = {}
        
    async def cog_load(self) -> None:
        """Initialize invite cache when cog loads."""
        await super().cog_load()
        for guild in self.bot.guilds:
            try:
                self.invites[guild.id] = {
                    invite.code: invite
                    for invite in await guild.invites()
                }
            except Exception as e:
                self.logger.error(f"Failed to cache invites for guild {guild.id}: {e}")
                
    @commands.Cog.listener()
    async def on_guild_join(self, guild: nextcord.Guild) -> None:
        """Cache invites when bot joins a new guild."""
        try:
            self.invites[guild.id] = {
                invite.code: invite
                for invite in await guild.invites()
            }
            self.logger.info(f"Cached invites for new guild {guild.id}")
        except Exception as e:
            self.logger.error(f"Failed to cache invites for new guild {guild.id}: {e}")
            
    @commands.Cog.listener()
    async def on_invite_create(self, invite: nextcord.Invite) -> None:
        """Update invite cache when a new invite is created."""
        self.invites[invite.guild.id][invite.code] = invite
        
    @commands.Cog.listener()
    async def on_invite_delete(self, invite: nextcord.Invite) -> None:
        """Update invite cache when an invite is deleted."""
        if invite.guild.id in self.invites:
            self.invites[invite.guild.id].pop(invite.code, None)
            
    async def _get_used_invite(self, guild: nextcord.Guild) -> Optional[nextcord.Invite]:
        """Determine which invite was used when a member joins."""
        try:
            # Get current invites
            current_invites = {
                invite.code: invite
                for invite in await guild.invites()
            }
            
            # Compare with cached invites
            for invite_code, invite in current_invites.items():
                cached_invite = self.invites[guild.id].get(invite_code)
                if cached_invite and invite.uses > cached_invite.uses:
                    # Update cache
                    self.invites[guild.id] = current_invites
                    return invite
                    
            return None
        except Exception as e:
            self.logger.error(f"Failed to determine used invite: {e}")
            return None
            
    @commands.Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        """Handle new member joins."""
        try:
            # Get used invite
            used_invite = await self._get_used_invite(member.guild)
            
            # Create welcome embed
            embed = EmbedBuilder.welcome_embed(
                member,
                f"{used_invite.inviter.mention} (`{used_invite.code}`)" if used_invite else None
            )
            
            # Send welcome message
            welcome_channel = member.guild.system_channel
            if welcome_channel and welcome_channel.permissions_for(member.guild.me).send_messages:
                await welcome_channel.send(embed=embed)
                
            # Store user data
            user_data = {
                "name": member.name,
                "discriminator": member.discriminator,
                "bot": member.bot,
                "invite_code": used_invite.code if used_invite else None,
                "inviter_id": used_invite.inviter.id if used_invite else None
            }
            await db.add_user(member.id, member.guild.id, user_data)
            
            # Track invite usage
            if used_invite:
                await db.track_invite({
                    "guild_id": member.guild.id,
                    "invite_code": used_invite.code,
                    "inviter_id": used_invite.inviter.id,
                    "user_id": member.id
                })
                
            # Log event
            await db.log_event(
                "member_join",
                member.guild.id,
                {
                    "user_id": member.id,
                    "invite_data": {
                        "code": used_invite.code if used_invite else None,
                        "inviter": used_invite.inviter.id if used_invite else None
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error handling member join for {member.id}: {e}")
            
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def invites(self, ctx: commands.Context) -> None:
        """Show invite statistics for the server."""
        try:
            stats = await db.get_invite_stats(ctx.guild.id)
            
            if not stats:
                await ctx.send(embed=EmbedBuilder.info_embed(
                    "Invite Statistics",
                    "No invites have been tracked yet."
                ))
                return
                
            # Create embed with invite stats
            embed = EmbedBuilder.default_embed(
                "Invite Statistics",
                f"Top inviters in {ctx.guild.name}"
            )
            
            for stat in stats[:10]:  # Show top 10
                inviter = ctx.guild.get_member(stat["_id"])
                if inviter:
                    embed.add_field(
                        name=f"{inviter.name}",
                        value=f"Invites: {stat['total_invites']}\n"
                              f"Last invite: <t:{int(stat['last_invite'].timestamp())}:R>",
                        inline=True
                    )
                    
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error showing invite stats: {e}")
            await ctx.send(embed=EmbedBuilder.error_embed("Failed to fetch invite statistics."))


def setup(bot: commands.Bot) -> None:
    """Set up the Welcome cog."""
    bot.add_cog(Welcome(bot)) 