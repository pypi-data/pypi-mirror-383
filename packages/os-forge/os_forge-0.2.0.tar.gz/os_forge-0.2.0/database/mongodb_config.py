"""
MongoDB Configuration for OS Forge
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConfig:
    """MongoDB configuration and connection management"""
    
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DATABASE", "Os-forge")
        self.collection_name = os.getenv("MONGODB_COLLECTION", "detailsforOS")
        
        if not self.uri:
            raise ValueError("MONGODB_URI environment variable is required")
        
        # Connection settings
        self.max_pool_size = 50
        self.min_pool_size = 10
        self.max_idle_time_ms = 30000
        self.server_selection_timeout_ms = 5000
        self.connect_timeout_ms = 10000
        self.socket_timeout_ms = 20000
        
        self._client: Optional[AsyncIOMotorClient] = None
        self._sync_client: Optional[MongoClient] = None
        self._database = None
        self._sync_database = None
    
    async def get_async_client(self) -> AsyncIOMotorClient:
        """Get async MongoDB client"""
        if self._client is None:
            self._client = AsyncIOMotorClient(
                self.uri,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                maxIdleTimeMS=self.max_idle_time_ms,
                serverSelectionTimeoutMS=self.server_selection_timeout_ms,
                connectTimeoutMS=self.connect_timeout_ms,
                socketTimeoutMS=self.socket_timeout_ms
            )
        return self._client
    
    def get_sync_client(self) -> MongoClient:
        """Get synchronous MongoDB client"""
        if self._sync_client is None:
            self._sync_client = MongoClient(
                self.uri,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                maxIdleTimeMS=self.max_idle_time_ms,
                serverSelectionTimeoutMS=self.server_selection_timeout_ms,
                connectTimeoutMS=self.connect_timeout_ms,
                socketTimeoutMS=self.socket_timeout_ms
            )
        return self._sync_client
    
    async def get_database(self):
        """Get MongoDB database (async)"""
        if self._database is None:
            client = await self.get_async_client()
            self._database = client[self.database_name]
        return self._database
    
    def get_sync_database(self):
        """Get MongoDB database (sync)"""
        if self._sync_database is None:
            client = self.get_sync_client()
            self._sync_database = client[self.database_name]
        return self._sync_database
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            client = await self.get_async_client()
            await client.admin.command('ping')
            logger.info("MongoDB connection successful")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    async def close_connections(self):
        """Close all MongoDB connections"""
        if self._client:
            self._client.close()
            self._client = None
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        self._database = None
        self._sync_database = None

# Global MongoDB configuration instance
mongodb_config = MongoDBConfig()
