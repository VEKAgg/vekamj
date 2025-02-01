"""Main entry point for the bot."""

import asyncio
import signal
import sys
from typing import Optional

from app.core.config import config
from app.core.logger import logger
from app.bot import VekaBot


class BotRunner:
    """Manages the bot's lifecycle."""
    
    def __init__(self):
        """Initialize the bot runner."""
        self.bot: Optional[VekaBot] = None
        self._shutdown = False
        
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}. Starting graceful shutdown...")
        self._shutdown = True
        if self.bot:
            asyncio.create_task(self.bot.close())
            
    async def start(self):
        """Start the bot."""
        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
            
            # Initialize and start bot
            self.bot = VekaBot()
            logger.info("Starting bot...")
            
            await self.bot.start(config.apis.discord_token)
        except asyncio.CancelledError:
            logger.info("Bot shutdown initiated...")
        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)
            sys.exit(1)
        finally:
            if self.bot:
                await self.cleanup()
                
    async def cleanup(self):
        """Clean up resources."""
        try:
            if not self.bot.is_closed():
                logger.info("Closing bot connection...")
                await self.bot.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)


async def main():
    """Main entry point."""
    runner = BotRunner()
    await runner.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1) 