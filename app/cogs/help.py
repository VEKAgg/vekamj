"""Help command cog for displaying command information."""

from typing import Dict, List, Optional

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.utils.embed_utils import EmbedBuilder


class Help(BaseCog):
    """Help command implementation."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.cmd_categories = {
            "Core": "Essential bot commands",
            "Moderation": "Server moderation commands",
            "Fun": "Entertainment commands",
            "Utility": "Useful utility commands",
            "Settings": "Bot configuration commands",
            "Info": "Information commands"
        }
        
    def get_command_category(self, command: commands.Command) -> str:
        """Get the category for a command based on its cog."""
        if not command.cog:
            return "Uncategorized"
        return command.cog.qualified_name
        
    def get_command_signature(self, command: commands.Command) -> str:
        """Get the command signature with parameters."""
        params = []
        for param in command.clean_params.values():
            if param.default == param.empty:
                params.append(f"<{param.name}>")
            else:
                params.append(f"[{param.name}]")
                
        return f"{command.name} {' '.join(params)}".strip()
        
    @commands.group(invoke_without_command=True)
    async def help(self, ctx: commands.Context, *, command_name: str = None):
        """Show help about bot commands.
        
        Use !help <command> for detailed help about a command.
        Use !help <category> to list commands in a category.
        """
        if command_name is None:
            await self.send_help_overview(ctx)
        else:
            # Check if it's a category
            category = command_name.title()
            if category in self.cmd_categories:
                await self.send_category_help(ctx, category)
                return
                
            # Check if it's a command
            command = self.bot.get_command(command_name)
            if command:
                await self.send_command_help(ctx, command)
            else:
                await ctx.send(f"No command or category called '{command_name}' found.")
                
    async def send_help_overview(self, ctx: commands.Context):
        """Send the main help overview."""
        embed = EmbedBuilder.default_embed(
            title="VEKA Bot Help",
            description="Here are all the command categories. Use `!help <category>` for more details."
        )
        
        # Add categories
        for category, description in self.cmd_categories.items():
            # Count commands in this category
            commands_in_category = [
                cmd for cmd in self.bot.commands
                if self.get_command_category(cmd) == category
            ]
            if commands_in_category:
                embed.add_field(
                    name=f"{category} Commands",
                    value=f"{description}\n`{len(commands_in_category)} commands`",
                    inline=False
                )
                
        embed.set_footer(text="Type !help <command> for more info on a command.")
        await ctx.send(embed=embed)
        
    async def send_category_help(self, ctx: commands.Context, category: str):
        """Send help for a specific category."""
        commands_in_category = [
            cmd for cmd in self.bot.commands
            if self.get_command_category(cmd) == category
        ]
        
        if not commands_in_category:
            await ctx.send(f"No commands found in category '{category}'.")
            return
            
        embed = EmbedBuilder.default_embed(
            title=f"{category} Commands",
            description=self.cmd_categories.get(category, "No description available.")
        )
        
        # Sort commands by name
        commands_in_category.sort(key=lambda x: x.name)
        
        # Add each command
        for cmd in commands_in_category:
            if cmd.hidden:
                continue
                
            signature = self.get_command_signature(cmd)
            brief = cmd.brief or cmd.help.split('\n')[0] if cmd.help else "No description"
            
            embed.add_field(
                name=signature,
                value=brief,
                inline=False
            )
            
        embed.set_footer(text="Type !help <command> for more info on a command.")
        await ctx.send(embed=embed)
        
    async def send_command_help(self, ctx: commands.Context, command: commands.Command):
        """Send help for a specific command."""
        embed = EmbedBuilder.default_embed(
            title=f"Command: {command.name}",
            description=command.help or "No description available."
        )
        
        # Add usage
        embed.add_field(
            name="Usage",
            value=f"```!{self.get_command_signature(command)}```",
            inline=False
        )
        
        # Add aliases if any
        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(f"`{alias}`" for alias in command.aliases),
                inline=False
            )
            
        # Add cooldown if any
        if command._buckets and command._buckets._cooldown:
            embed.add_field(
                name="Cooldown",
                value=f"{command._buckets._cooldown.rate} uses every {command._buckets._cooldown.per} seconds",
                inline=False
            )
            
        # Add permissions if any
        if command.checks:
            perms = []
            for check in command.checks:
                if isinstance(check, commands.has_permissions):
                    perms.extend(
                        perm.replace('_', ' ').title()
                        for perm, value in check.permissions.items()
                        if value
                    )
            if perms:
                embed.add_field(
                    name="Required Permissions",
                    value=", ".join(f"`{perm}`" for perm in perms),
                    inline=False
                )
                
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Set up the Help cog."""
    bot.add_cog(Help(bot)) 