from typing import Optional

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog

class General(BaseCog):
    """General purpose commands."""
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Get the bot's current websocket latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")
        
    @commands.command()
    async def info(self, ctx: commands.Context):
        """Get information about the bot."""
        embed = nextcord.Embed(
            title="Bot Information",
            description="A modern Discord bot built with nextcord",
            color=nextcord.Color.blue()
        )
        
        # Add bot statistics
        embed.add_field(
            name="Statistics",
            value=f"Servers: {len(self.bot.guilds)}\n"
                  f"Users: {sum(g.member_count for g in self.bot.guilds)}\n"
                  f"Commands: {len(self.bot.commands)}",
            inline=False
        )
        
        # Add system information
        embed.add_field(
            name="System",
            value=f"Python: {nextcord.__version__}\n"
                  f"Nextcord: {nextcord.__version__}",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def help(self, ctx: commands.Context, *, command: Optional[str] = None):
        """Show help for a command or list all commands."""
        if command is None:
            embed = nextcord.Embed(
                title="Command List",
                description="Here are all available commands:",
                color=nextcord.Color.green()
            )
            
            for cog_name, cog in self.bot.cogs.items():
                # Skip if cog has no commands
                if not cog.get_commands():
                    continue
                    
                # Add cog commands to embed
                command_list = "\n".join(f"`{c.name}` - {c.short_doc}" for c in cog.get_commands())
                embed.add_field(
                    name=cog_name,
                    value=command_list or "No commands available",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            return
            
        # Get specific command help
        cmd = self.bot.get_command(command)
        if cmd is None:
            await ctx.send(f"Command `{command}` not found.")
            return
            
        await ctx.send(self.format_help(cmd))

def setup(bot: commands.Bot):
    """Setup function for the cog."""
    bot.add_cog(General(bot)) 