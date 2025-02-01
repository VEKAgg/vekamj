"""MongoDB database module for async database operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import config
from app.core.logger import logger


class MongoDB:
    """MongoDB database manager."""
    
    def __init__(self):
        """Initialize database connection."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self) -> None:
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(config.database.mongodb.uri)
            self.db = self.client[config.database.mongodb.database]
            # Ping database to verify connection
            await self.db.command("ping")
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
            
    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
            
    # User Management
    async def add_user(self, user_id: int, guild_id: int, data: Dict[str, Any]) -> None:
        """Add a new user to the database."""
        collection = self.db["users"]
        data.update({
            "user_id": user_id,
            "guild_id": guild_id,
            "joined_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        })
        await collection.update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": data},
            upsert=True
        )
        
    async def get_user(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from database."""
        collection = self.db["users"]
        return await collection.find_one({"user_id": user_id, "guild_id": guild_id})
        
    async def update_user_activity(self, user_id: int, guild_id: int, activity_data: Dict[str, Any]) -> None:
        """Update user activity data."""
        collection = self.db["user_activities"]
        activity_data.update({
            "user_id": user_id,
            "guild_id": guild_id,
            "timestamp": datetime.utcnow()
        })
        await collection.insert_one(activity_data)
        
        # Update last active timestamp
        await self.db["users"].update_one(
            {"user_id": user_id, "guild_id": guild_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
        
    # Invite Tracking
    async def track_invite(self, invite_data: Dict[str, Any]) -> None:
        """Track an invite use."""
        collection = self.db["invites"]
        await collection.insert_one({
            **invite_data,
            "timestamp": datetime.utcnow()
        })
        
    async def get_invite_stats(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get invite statistics for a guild."""
        collection = self.db["invites"]
        pipeline = [
            {"$match": {"guild_id": guild_id}},
            {"$group": {
                "_id": "$inviter_id",
                "total_invites": {"$sum": 1},
                "last_invite": {"$max": "$timestamp"}
            }},
            {"$sort": {"total_invites": -1}}
        ]
        return await collection.aggregate(pipeline).to_list(None)
        
    # Event Logging
    async def log_event(self, event_type: str, guild_id: int, data: Dict[str, Any]) -> None:
        """Log an event to the database."""
        collection = self.db["events"]
        await collection.insert_one({
            "type": event_type,
            "guild_id": guild_id,
            "timestamp": datetime.utcnow(),
            "data": data
        })
        
    async def get_recent_events(self, guild_id: int, event_type: Optional[str] = None, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events from the database."""
        collection = self.db["events"]
        query = {"guild_id": guild_id}
        if event_type:
            query["type"] = event_type
            
        return await collection.find(query) \
                             .sort("timestamp", -1) \
                             .limit(limit) \
                             .to_list(None)


# Global database instance
db = MongoDB() 