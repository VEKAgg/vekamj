"""Redis database module for caching and rate limiting."""

import asyncio
from typing import Any, Optional, Union

import redis.asyncio as redis

from app.core.config import config
from app.core.logger import logger


class RedisManager:
    """Manages Redis connection and operations."""
    
    def __init__(self):
        """Initialize Redis manager."""
        self._redis: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()
        
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._redis is not None
        
    async def connect(self) -> None:
        """Connect to Redis."""
        if self.is_connected:
            return
            
        async with self._lock:
            try:
                self._redis = await redis.from_url(
                    config.db.redis_uri,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self._redis.ping()
                logger.info("Connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._redis = None
                raise
                
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Closed Redis connection")
            
    async def _ensure_connected(self) -> None:
        """Ensure Redis is connected before operations."""
        if not self.is_connected:
            await self.connect()
            
    def _build_key(self, key: str) -> str:
        """Build Redis key with prefix."""
        return f"{config.db.redis_prefix}{key}"
        
    async def set(
        self,
        key: str,
        value: Union[str, int, float, bool],
        expire: Optional[int] = None
    ) -> None:
        """Set a key-value pair in Redis.
        
        Args:
            key: The key to set
            value: The value to set
            expire: Optional expiration time in seconds
        """
        await self._ensure_connected()
        key = self._build_key(key)
        await self._redis.set(key, value, ex=expire)
        
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis.
        
        Args:
            key: The key to get
            
        Returns:
            The value if it exists, None otherwise
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.get(key)
        
    async def delete(self, key: str) -> None:
        """Delete a key from Redis.
        
        Args:
            key: The key to delete
        """
        await self._ensure_connected()
        key = self._build_key(key)
        await self._redis.delete(key)
        
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.exists(key)
        
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a key's value.
        
        Args:
            key: The key to increment
            amount: Amount to increment by
            
        Returns:
            The new value
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.incrby(key, amount)
        
    async def set_add(self, key: str, *values: Any) -> int:
        """Add values to a Redis set.
        
        Args:
            key: The set key
            *values: Values to add
            
        Returns:
            Number of values added
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.sadd(key, *values)
        
    async def set_remove(self, key: str, *values: Any) -> int:
        """Remove values from a Redis set.
        
        Args:
            key: The set key
            *values: Values to remove
            
        Returns:
            Number of values removed
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.srem(key, *values)
        
    async def set_members(self, key: str) -> set:
        """Get all members of a Redis set.
        
        Args:
            key: The set key
            
        Returns:
            Set of members
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.smembers(key)
        
    async def hash_set(self, key: str, mapping: dict) -> None:
        """Set multiple hash fields.
        
        Args:
            key: The hash key
            mapping: Dictionary of field-value pairs
        """
        await self._ensure_connected()
        key = self._build_key(key)
        await self._redis.hmset(key, mapping)
        
    async def hash_get(self, key: str, field: str) -> Optional[str]:
        """Get a hash field.
        
        Args:
            key: The hash key
            field: The field to get
            
        Returns:
            The field value if it exists, None otherwise
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.hget(key, field)
        
    async def hash_get_all(self, key: str) -> dict:
        """Get all fields and values in a hash.
        
        Args:
            key: The hash key
            
        Returns:
            Dictionary of all field-value pairs
        """
        await self._ensure_connected()
        key = self._build_key(key)
        return await self._redis.hgetall(key)


# Create global Redis manager instance
redis = RedisManager() 