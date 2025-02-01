"""Fun commands for entertainment and engagement."""

import random
import aiohttp
from typing import Optional, Dict

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.utils.embed_utils import EmbedBuilder
from app.core.config import config


class Fun(BaseCog):
    """Fun commands for entertainment."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.session = aiohttp.ClientSession()
        
    def cog_unload(self):
        """Clean up resources."""
        self.bot.loop.create_task(self.session.close())
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dadjoke(self, ctx: commands.Context):
        """Get a random dad joke."""
        async with self.session.get(
            "https://icanhazdadjoke.com/",
            headers={"Accept": "application/json"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                joke = data["joke"]
                
                embed = EmbedBuilder.default_embed(
                    title="👨 Dad Joke",
                    description=joke
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch a dad joke. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx: commands.Context):
        """Fetch a meme from Reddit."""
        subreddits = ["memes", "dankmemes", "wholesomememes"]
        subreddit = random.choice(subreddits)
        
        async with self.session.get(
            f"https://www.reddit.com/r/{subreddit}/random/.json"
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                # Handle both types of Reddit API responses
                if isinstance(data, list):
                    post = data[0]["data"]["children"][0]["data"]
                else:
                    post = data["data"]["children"][0]["data"]
                    
                if post["over_18"]:  # Skip NSFW content
                    return await self.meme(ctx)
                    
                embed = EmbedBuilder.default_embed(
                    title=post["title"][:256],
                    url=f"https://reddit.com{post['permalink']}"
                )
                embed.set_image(url=post["url"])
                embed.set_footer(text=f"👍 {post['ups']} | 💬 {post['num_comments']} | 📍 r/{subreddit}")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch a meme. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gif(self, ctx: commands.Context, *, search: str):
        """Search for a GIF.
        
        Example: !gif cute cats
        """
        try:
            async with self.session.get(
                "https://api.giphy.com/v1/gifs/search",
                params={
                    "api_key": config.apis.giphy_key,
                    "q": search,
                    "limit": 10,
                    "rating": "g"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["data"]:
                        gif = random.choice(data["data"])
                        await ctx.send(gif["images"]["original"]["url"])
                    else:
                        await ctx.send(f"No GIFs found for: {search}")
                else:
                    await ctx.send("Failed to fetch a GIF. Try again later!")
        except Exception as e:
            await ctx.send("An error occurred while fetching the GIF.")
            
    @commands.command()
    async def ship(self, ctx: commands.Context, user1: nextcord.Member, user2: nextcord.Member):
        """Calculate the compatibility between two users.
        
        Example: !ship @user1 @user2
        """
        # Generate a consistent ship percentage based on user IDs
        ship_seed = int(str(user1.id) + str(user2.id))
        random.seed(ship_seed)
        percentage = random.randint(0, 100)
        
        # Create heart bar
        hearts = int(percentage / 10)
        heart_bar = "❤️" * hearts + "🖤" * (10 - hearts)
        
        embed = EmbedBuilder.default_embed(
            title="💘 Shipping Results",
            description=f"{user1.mention} x {user2.mention}"
        )
        
        embed.add_field(
            name="Compatibility",
            value=f"{percentage}%\n{heart_bar}",
            inline=False
        )
        
        # Add a cute message based on percentage
        if percentage >= 90:
            message = "A perfect match! 💝"
        elif percentage >= 70:
            message = "Great compatibility! 💖"
        elif percentage >= 45:
            message = "There's potential! 💗"
        elif percentage >= 20:
            message = "Might need some work... 💔"
        else:
            message = "Yikes... Maybe just be friends? 💢"
            
        embed.add_field(name="Verdict", value=message, inline=False)
        await ctx.send(embed=embed)
        
    @commands.command()
    async def rps(self, ctx: commands.Context, choice: str):
        """Play Rock-Paper-Scissors.
        
        Example: !rps rock
        """
        choice = choice.lower()
        choices = ["rock", "paper", "scissors"]
        
        if choice not in choices:
            await ctx.send("Please choose either rock, paper, or scissors!")
            return
            
        bot_choice = random.choice(choices)
        
        # Determine winner
        if choice == bot_choice:
            result = "Tie"
            color = 0xFFFF00
        elif (
            (choice == "rock" and bot_choice == "scissors") or
            (choice == "paper" and bot_choice == "rock") or
            (choice == "scissors" and bot_choice == "paper")
        ):
            result = "You win"
            color = 0x00FF00
        else:
            result = "I win"
            color = 0xFF0000
            
        # Create embed
        embed = nextcord.Embed(title="Rock Paper Scissors", color=color)
        embed.add_field(name="Your Choice", value=choice.title(), inline=True)
        embed.add_field(name="My Choice", value=bot_choice.title(), inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def lmgtfy(self, ctx: commands.Context, *, query: str):
        """Generate a "Let Me Google That For You" link.
        
        Example: !lmgtfy how to tie a tie
        """
        url = f"https://letmegooglethat.com/?q={query.replace(' ', '+')}"
        await ctx.send(f"Here you go: {url}")
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def catfact(self, ctx: commands.Context):
        """Get a random cat fact."""
        async with self.session.get("https://catfact.ninja/fact") as response:
            if response.status == 200:
                data = await response.json()
                
                embed = EmbedBuilder.default_embed(
                    title="🐱 Random Cat Fact",
                    description=data["fact"]
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch a cat fact. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dogfact(self, ctx: commands.Context):
        """Get a random dog fact."""
        async with self.session.get("https://dog-api.kinduff.com/api/facts") as response:
            if response.status == 200:
                data = await response.json()
                
                embed = EmbedBuilder.default_embed(
                    title="🐕 Random Dog Fact",
                    description=data["facts"][0]
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch a dog fact. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def horoscope(self, ctx: commands.Context, sign: str):
        """Get your daily horoscope.
        
        Example: !horoscope aries
        """
        sign = sign.lower()
        valid_signs = [
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
        ]
        
        if sign not in valid_signs:
            await ctx.send("Please provide a valid zodiac sign!")
            return
            
        # Using aztro API (requires rapid API key)
        url = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"
        headers = {
            "X-RapidAPI-Host": "sameer-kumar-aztro-v1.p.rapidapi.com",
            "X-RapidAPI-Key": config.apis.rapidapi_key
        }
        
        async with self.session.post(
            url,
            headers=headers,
            params={"sign": sign, "day": "today"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                embed = EmbedBuilder.default_embed(
                    title=f"Daily Horoscope for {sign.title()}",
                    description=data["description"]
                )
                
                embed.add_field(name="Mood", value=data["mood"], inline=True)
                embed.add_field(name="Lucky Number", value=data["lucky_number"], inline=True)
                embed.add_field(name="Lucky Time", value=data["lucky_time"], inline=True)
                embed.add_field(name="Color", value=data["color"], inline=True)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch horoscope. Try again later!")
                
    @commands.command()
    async def randomcolor(self, ctx: commands.Context):
        """Display a random color with hex code."""
        color = random.randint(0, 0xFFFFFF)
        hex_code = f"#{color:06X}"
        
        embed = nextcord.Embed(
            title="🎨 Random Color",
            description=f"Hex Code: `{hex_code}`",
            color=color
        )
        
        # Create a solid color image
        embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{hex_code[1:]}/100x100")
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def hack(self, ctx: commands.Context, user: nextcord.Member):
        """Fake hacking prank.
        
        Example: !hack @user
        """
        msg = await ctx.send(f"Hacking {user.name}....")
        await ctx.trigger_typing()
        
        messages = [
            "Finding Discord login...",
            "Bypassing 2FA...",
            "Finding IP address...",
            "Selling data to the dark web...",
            "Downloading virus.exe...",
            "Deleting System32...",
            "Exposing DMs...",
            "Just kidding! 😉"
        ]
        
        for message in messages:
            await msg.edit(content=message)
            await asyncio.sleep(1.5)
            
    @commands.command()
    async def howgay(self, ctx: commands.Context, user: nextcord.Member = None):
        """Calculate how gay someone is (100% accurate).
        
        Example: !howgay @user
        """
        user = user or ctx.author
        
        # Generate consistent percentage based on user ID
        random.seed(user.id)
        percentage = random.randint(0, 100)
        
        embed = EmbedBuilder.default_embed(
            title="🌈 Gay Calculator",
            description=f"{user.mention} is {percentage}% gay!"
        )
        
        # Add rainbow bar
        bar_length = 10
        filled = int((percentage / 100) * bar_length)
        bar = "🌈" * filled + "⬜" * (bar_length - filled)
        
        embed.add_field(name="Gay Level", value=bar, inline=False)
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def simp(self, ctx: commands.Context, user: nextcord.Member = None):
        """Calculate someone's simp level.
        
        Example: !simp @user
        """
        user = user or ctx.author
        
        # Generate consistent percentage based on user ID
        random.seed(user.id)
        percentage = random.randint(0, 100)
        
        embed = EmbedBuilder.default_embed(
            title="💝 Simp Calculator",
            description=f"{user.mention}'s simp level is {percentage}%!"
        )
        
        # Add simp bar
        bar_length = 10
        filled = int((percentage / 100) * bar_length)
        bar = "💖" * filled + "🖤" * (bar_length - filled)
        
        embed.add_field(name="Simp Level", value=bar, inline=False)
        
        # Add funny verdict
        if percentage >= 90:
            verdict = "Ultimate Simp! Touch some grass!"
        elif percentage >= 70:
            verdict = "Major Simp Energy!"
        elif percentage >= 45:
            verdict = "Moderate Simping Detected!"
        elif percentage >= 20:
            verdict = "Slight Simp Tendencies..."
        else:
            verdict = "Not a Simp... Impressive!"
            
        embed.add_field(name="Verdict", value=verdict, inline=False)
        
        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Set up the Fun cog."""
    bot.add_cog(Fun(bot)) 