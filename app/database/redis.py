"""Redis database module with fallback mechanisms."""

from typing import Any, Optional, Union
import time
from datetime import datetime
import warnings

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import config
from app.core.logger import logger


class RedisManager:
    """Redis connection manager with fallback mechanisms."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis: Optional[Redis] = None
        self._prefix = config.database.redis.prefix
        self._memory_store = {}  # Simple in-memory fallback
        self._available = False
        
    async def connect(self) -> None:
        """Connect to Redis with fallback."""
        try:
            self.redis = redis.from_url(
                config.database.redis.uri,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            self._available = True
            logger.info("Successfully connected to Redis")
        except Exception as e:
            self._available = False
            warnings.warn(
                f"Redis connection failed: {e}. Using in-memory fallback. "
                "This is not recommended for production!"
            )
            
    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis and self._available:
            await self.redis.close()
            logger.info("Closed Redis connection")
        self._memory_store.clear()
            
    def _key(self, key: str) -> str:
        """Create prefixed key."""
        return f"{self._prefix}{key}"
        
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        """Set a key with optional expiration."""
        key = self._key(key)
        if self._available:
            await self.redis.set(key, value, ex=expire)
        else:
            # Simple in-memory fallback with expiration
            self._memory_store[key] = {
                'value': value,
                'expire': time.time() + expire if expire else None
            }
            
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        key = self._key(key)
        if self._available:
            return await self.redis.get(key)
        else:
            # Check expiration for in-memory store
            data = self._memory_store.get(key)
            if data:
                if data['expire'] and time.time() > data['expire']:
                    del self._memory_store[key]
                    return None
                return data['value']
            return None
            
    async def delete(self, key: str) -> None:
        """Delete a key."""
        key = self._key(key)
        if self._available:
            await self.redis.delete(key)
        else:
            self._memory_store.pop(key, None)
            
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        key = self._key(key)
        if self._available:
            return await self.redis.exists(key) > 0
        else:
            # Check expiration for in-memory store
            data = self._memory_store.get(key)
            if data and data['expire'] and time.time() > data['expire']:
                del self._memory_store[key]
                return False
            return key in self._memory_store
            
    async def increment(self, key: str) -> int:
        """Increment a counter."""
        key = self._key(key)
        if self._available:
            return await self.redis.incr(key)
        else:
            # Simple in-memory increment
            data = self._memory_store.get(key, {'value': '0'})
            new_value = int(data['value']) + 1
            self._memory_store[key] = {
                'value': str(new_value),
                'expire': data.get('expire')
            }
            return new_value
            
    async def check_cooldown(self, user_id: int, command: str, cooldown: int) -> bool:
        """Check if user is in cooldown with fallback."""
        key = f"cooldown:{user_id}:{command}"
        if await self.exists(key):
            return False
        await self.set(key, "1", expire=cooldown)
        return True
            
    async def cache_get(self, key: str, factory: callable, expire: Optional[int] = None) -> Any:
        """Get or create cached value with fallback."""
        cached = await self.get(key)
        if cached is not None:
            return cached
            
        value = await factory()
        if value is not None:
            await self.set(key, value, expire)
        return value
            
    # Guild settings with fallback
    async def get_guild_setting(self, guild_id: int, key: str) -> Optional[str]:
        """Get a guild setting."""
        return await self.get(f"guild:{guild_id}:setting:{key}")
        
    async def set_guild_setting(self, guild_id: int, key: str, value: str) -> None:
        """Set a guild setting."""
        await self.set(f"guild:{guild_id}:setting:{key}", value)
        
    async def delete_guild_setting(self, guild_id: int, key: str) -> None:
        """Delete a guild setting."""
        await self.delete(f"guild:{guild_id}:setting:{key}")
        
    async def set_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Set rate limit for a key."""
        key = self._key(f"ratelimit:{key}")
        count = await self.redis.incr(key)
        
        if count == 1:
            await self.redis.expire(key, window)
            
        return count <= limit
        
    async def cache_delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        pattern = self._key(pattern)
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


# Global Redis instance
redis = RedisManager() 