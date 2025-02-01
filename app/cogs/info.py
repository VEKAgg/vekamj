"""Informational commands with various API integrations."""

import aiohttp
from typing import Optional, Dict
from datetime import datetime

import nextcord
from nextcord.ext import commands

from app.cogs.base import BaseCog
from app.utils.embed_utils import EmbedBuilder
from app.core.config import config


class Info(BaseCog):
    """Informational commands with API integrations."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.session = aiohttp.ClientSession()
        
    def cog_unload(self):
        """Clean up resources."""
        self.bot.loop.create_task(self.session.close())
        
    @commands.command()
    async def botupdates(self, ctx: commands.Context):
        """Show bot updates & GitHub link."""
        embed = EmbedBuilder.default_embed(
            title="Bot Updates & Information",
            description="Stay up to date with the latest changes and improvements!"
        )
        
        embed.add_field(
            name="GitHub Repository",
            value="[View Source Code](https://github.com/yourusername/veka-bot)",
            inline=False
        )
        
        embed.add_field(
            name="Latest Updates",
            value="• Added new fun commands\n• Improved error handling\n• Enhanced performance",
            inline=False
        )
        
        embed.add_field(
            name="Planned Features",
            value="• Web dashboard\n• More game integrations\n• Custom server settings",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quote(self, ctx: commands.Context, *, query: Optional[str] = None):
        """Fetch a quote by author or keyword.
        
        Example: !quote Einstein
        """
        params = {}
        if query:
            params["q"] = query
            
        async with self.session.get(
            "https://api.quotable.io/random",
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                embed = EmbedBuilder.default_embed(
                    title="📜 Random Quote",
                    description=f"*{data['content']}*"
                )
                
                embed.add_field(
                    name="Author",
                    value=data["author"],
                    inline=True
                )
                if "tags" in data and data["tags"]:
                    embed.add_field(
                        name="Tags",
                        value=", ".join(data["tags"]),
                        inline=True
                    )
                    
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch a quote. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def news(self, ctx: commands.Context, *, topic: str = None):
        """Fetch latest news headlines.
        
        Example: !news technology
        """
        params = {
            "apiKey": config.apis.newsapi_key,
            "language": "en",
            "pageSize": 5
        }
        
        if topic:
            params["q"] = topic
            
        async with self.session.get(
            "https://newsapi.org/v2/top-headlines",
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                if not data["articles"]:
                    await ctx.send("No news found for this topic.")
                    return
                    
                embed = EmbedBuilder.default_embed(
                    title=f"📰 Latest News" + (f" - {topic}" if topic else ""),
                    description="Here are the latest headlines:"
                )
                
                for article in data["articles"]:
                    embed.add_field(
                        name=article["title"],
                        value=f"[Read More]({article['url']})\n{article['description'][:100]}...",
                        inline=False
                    )
                    
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch news. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def crypto(self, ctx: commands.Context, symbol: str):
        """Display cryptocurrency prices.
        
        Example: !crypto BTC
        """
        symbol = symbol.upper()
        
        async with self.session.get(
            f"https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": symbol.lower(),
                "vs_currencies": "usd,eur",
                "include_24hr_change": "true"
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                if not data:
                    await ctx.send(f"Cryptocurrency {symbol} not found!")
                    return
                    
                crypto_data = next(iter(data.values()))
                
                embed = EmbedBuilder.default_embed(
                    title=f"💰 {symbol} Price",
                    description="Current cryptocurrency prices and changes"
                )
                
                embed.add_field(
                    name="USD",
                    value=f"${crypto_data['usd']:,.2f}",
                    inline=True
                )
                embed.add_field(
                    name="EUR",
                    value=f"€{crypto_data['eur']:,.2f}",
                    inline=True
                )
                
                if "usd_24h_change" in crypto_data:
                    change = crypto_data["usd_24h_change"]
                    emoji = "📈" if change > 0 else "📉"
                    embed.add_field(
                        name="24h Change",
                        value=f"{emoji} {change:.2f}%",
                        inline=True
                    )
                    
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch cryptocurrency data. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stock(self, ctx: commands.Context, symbol: str):
        """Show stock market prices.
        
        Example: !stock AAPL
        """
        symbol = symbol.upper()
        
        # Using Alpha Vantage API
        async with self.session.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": config.apis.alphavantage_key
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                if "Global Quote" not in data or not data["Global Quote"]:
                    await ctx.send(f"Stock {symbol} not found!")
                    return
                    
                quote = data["Global Quote"]
                
                embed = EmbedBuilder.default_embed(
                    title=f"📈 {symbol} Stock Price",
                    description="Current stock market data"
                )
                
                price = float(quote["05. price"])
                change = float(quote["09. change"])
                change_percent = float(quote["10. change percent"].rstrip("%"))
                
                embed.add_field(
                    name="Price",
                    value=f"${price:,.2f}",
                    inline=True
                )
                
                emoji = "📈" if change > 0 else "📉"
                embed.add_field(
                    name="Change",
                    value=f"{emoji} ${change:,.2f} ({change_percent:,.2f}%)",
                    inline=True
                )
                
                embed.add_field(
                    name="Volume",
                    value=f"{int(quote['06. volume']):,}",
                    inline=True
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch stock data. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dictionary(self, ctx: commands.Context, *, word: str):
        """Fetch word definitions.
        
        Example: !dictionary example
        """
        # Using Free Dictionary API
        async with self.session.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                if not data:
                    await ctx.send(f"No definition found for '{word}'")
                    return
                    
                entry = data[0]
                
                embed = EmbedBuilder.default_embed(
                    title=f"📚 Definition: {word}",
                    description=entry.get("phonetic", "")
                )
                
                for meaning in entry["meanings"][:3]:  # Limit to 3 meanings
                    definitions = meaning["definitions"][:2]  # Limit to 2 definitions per type
                    value = "\n".join(
                        f"• {d['definition']}"
                        for d in definitions
                    )
                    
                    embed.add_field(
                        name=f"({meaning['partOfSpeech']})",
                        value=value,
                        inline=False
                    )
                    
                if "sourceUrls" in entry and entry["sourceUrls"]:
                    embed.add_field(
                        name="Source",
                        value=f"[Dictionary Link]({entry['sourceUrls'][0]})",
                        inline=False
                    )
                    
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No definition found for '{word}'")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def translate(self, ctx: commands.Context, lang: str, *, text: str):
        """Translate text to another language.
        
        Example: !translate es Hello, how are you?
        """
        # Using LibreTranslate API
        async with self.session.post(
            "https://libretranslate.de/translate",
            json={
                "q": text,
                "source": "auto",
                "target": lang
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                embed = EmbedBuilder.default_embed(
                    title="🌐 Translation",
                    description=f"Translation to {lang.upper()}"
                )
                
                embed.add_field(
                    name="Original",
                    value=text,
                    inline=False
                )
                embed.add_field(
                    name="Translation",
                    value=data["translatedText"],
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to translate text. Make sure you're using a valid language code (e.g., 'es' for Spanish).")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def wiki(self, ctx: commands.Context, *, query: str):
        """Get Wikipedia summary.
        
        Example: !wiki Python programming language
        """
        # Using Wikipedia API
        async with self.session.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "titles": query,
                "prop": "extracts|info",
                "exintro": True,
                "explaintext": True,
                "inprop": "url",
                "redirects": 1
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                page = next(iter(data["query"]["pages"].values()))
                
                if "missing" in page:
                    await ctx.send(f"No Wikipedia article found for '{query}'")
                    return
                    
                # Truncate description if too long
                description = page["extract"][:1000]
                if len(page["extract"]) > 1000:
                    description += "..."
                    
                embed = EmbedBuilder.default_embed(
                    title=page["title"],
                    description=description
                )
                
                embed.add_field(
                    name="Read More",
                    value=f"[Wikipedia Link]({page['fullurl']})",
                    inline=False
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch Wikipedia article. Try again later!")
                
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx: commands.Context, *, query: str):
        """Display song lyrics.
        
        Example: !lyrics Never Gonna Give You Up
        """
        # Using Genius API
        headers = {"Authorization": f"Bearer {config.apis.genius_key}"}
        
        # First, search for the song
        async with self.session.get(
            "https://api.genius.com/search",
            headers=headers,
            params={"q": query}
        ) as response:
            if response.status == 200:
                data = await response.json()
                
                if not data["response"]["hits"]:
                    await ctx.send(f"No lyrics found for '{query}'")
                    return
                    
                song = data["response"]["hits"][0]["result"]
                
                embed = EmbedBuilder.default_embed(
                    title=f"🎵 {song['title']}",
                    description=f"by {song['primary_artist']['name']}"
                )
                
                embed.add_field(
                    name="View Lyrics",
                    value=f"[Click Here]({song['url']})",
                    inline=False
                )
                
                if song.get("song_art_image_url"):
                    embed.set_thumbnail(url=song["song_art_image_url"])
                    
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to fetch lyrics. Try again later!")


def setup(bot: commands.Bot) -> None:
    """Set up the Info cog."""
    bot.add_cog(Info(bot)) 