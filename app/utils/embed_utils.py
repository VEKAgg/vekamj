"""Utility module for creating standardized embed messages."""

from datetime import datetime
from typing import Optional, Union

import nextcord
from nextcord import Embed, Member, User

class EmbedBuilder:
    """Helper class for building consistent embed messages."""
    
    @staticmethod
    def default_embed(title: str, description: Optional[str] = None) -> Embed:
        """Create a default styled embed with consistent branding."""
        embed = Embed(
            title=title,
            description=description,
            color=nextcord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="VEKA Bot")
        return embed
    
    @staticmethod
    def welcome_embed(member: Member, invite_used: Optional[str] = None) -> Embed:
        """Create a welcome embed for new members."""
        embed = Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=f"Welcome {member.mention}! We're glad to have you here!",
            color=nextcord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )
        if invite_used:
            embed.add_field(name="Invited By", value=invite_used, inline=True)
        embed.set_footer(text=f"Member #{len(member.guild.members)}")
        return embed
    
    @staticmethod
    def error_embed(error_message: str) -> Embed:
        """Create an error embed."""
        return Embed(
            title="Error",
            description=error_message,
            color=nextcord.Color.red(),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def success_embed(message: str) -> Embed:
        """Create a success embed."""
        return Embed(
            title="Success",
            description=message,
            color=nextcord.Color.green(),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def info_embed(title: str, message: str) -> Embed:
        """Create an info embed."""
        return Embed(
            title=title,
            description=message,
            color=nextcord.Color.blue(),
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def activity_embed(member: Member, activity: nextcord.Activity) -> Embed:
        """Create an activity update embed."""
        activity_type = activity.type.name.title()
        embed = Embed(
            title=f"{activity_type} Activity Update",
            description=f"{member.mention} is now {activity_type.lower()}",
            color=nextcord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name=activity_type, value=activity.name, inline=False)
        if hasattr(activity, "details") and activity.details:
            embed.add_field(name="Details", value=activity.details, inline=False)
        return embed

    @staticmethod
    def user_info_embed(user: Union[Member, User]) -> Embed:
        """Create a user info embed."""
        embed = Embed(
            title="User Information",
            color=nextcord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Basic info
        embed.add_field(
            name="User",
            value=f"{user.name} ({user.mention})",
            inline=False
        )
        embed.add_field(
            name="ID",
            value=user.id,
            inline=True
        )
        embed.add_field(
            name="Created",
            value=f"<t:{int(user.created_at.timestamp())}:R>",
            inline=True
        )
        
        # Member specific info
        if isinstance(user, Member):
            embed.add_field(
                name="Joined",
                value=f"<t:{int(user.joined_at.timestamp())}:R>",
                inline=True
            )
            roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
            if roles:
                embed.add_field(
                    name=f"Roles [{len(roles)}]",
                    value=" ".join(roles) if len(roles) <= 10 else " ".join(roles[:10]) + f" (+{len(roles)-10} more)",
                    inline=False
                )
        
        return embed 