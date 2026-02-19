from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (helps when using Atlas connection strings locally)
env_path = Path(__file__).parent.joinpath('.env')
if env_path.exists():
    load_dotenv(env_path)
else:
    # also load from project root .env if present
    root_env = Path(__file__).parent.parent.joinpath('.env')
    if root_env.exists():
        load_dotenv(root_env)

# MONGO_URI can be the Atlas connection string or a local Mongo URI
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "smart_attendance_db")


_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Return a cached MongoClient. Accepts MongoDB Atlas URIs.

    Example Atlas URI:
      mongodb+srv://<user>:<password>@cluster0.abcd.mongodb.net/?retryWrites=true&w=majority
    """
    global _client
    if _client is None:
        # Set serverSelectionTimeoutMS to fail fast when URI is unreachable
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    return get_client()[DB_NAME]


def get_collection(name: str) -> Collection:
    return get_db()[name]
