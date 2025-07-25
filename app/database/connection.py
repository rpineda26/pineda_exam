"""Database connection handler for MongoDB."""

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from app.logger import default_logger as logger
import config


class DatabaseConnection:
    """Handles MongoDB connection and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self._client: MongoClient = None
        self._database: Database = None
        self._collection: Collection = None
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self._client = MongoClient(config.MONGODB_URI)
            # Test connection
            self._client.admin.command('ping')
            self._database = self._client[config.DATABASE_NAME]
            self._collection = self._database[config.COLLECTION_NAME]
            logger.info("Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.critical(f"Failed to connect to MongoDB: {e}")
            return False
    
    def get_collection(self) -> Collection:
        """Get the tasks collection."""
        if self._collection is None:
            raise ConnectionError("Database not connected. Call connect() first.")
        return self._collection
    
    def close(self):
        """Close database connection."""
        if self._client:
            self._client.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()