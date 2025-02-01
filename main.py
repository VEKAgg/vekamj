import asyncio
import os

from dotenv import load_dotenv

from app.core.bot import VekaBot
from app.core.logger import logger

# Load environment variables
load_dotenv()

async def main():
    """Main entry point for the bot."""
    # Get token from environment variables
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        return

    # Create and run bot
    bot = VekaBot()
    try:
        logger.info("Starting bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await bot.close()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=e)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main()) 