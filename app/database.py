from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

# Load MongoDB URI from environment variable
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "journal_app"

if not MONGODB_URL:
    raise ValueError("❌ MONGODB_URL environment variable is not set")

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @property
    def users(self):
        return self.client[DATABASE_NAME]["users"]

    @property
    def journals(self):
        return self.client[DATABASE_NAME]["journals"]

db_instance = Database()

async def connect_to_mongo():
    """Connect to MongoDB on startup"""
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    print(f"✅ Connected to MongoDB Atlas!")

async def close_mongo_connection():
    """Close MongoDB connection on shutdown"""
    if db_instance.client:
        db_instance.client.close()
        print("🛑 Closed MongoDB connection")

db = db_instance
