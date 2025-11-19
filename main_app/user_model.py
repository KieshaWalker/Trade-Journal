import os
from time import timezone 
from django.contrib.auth.models import User
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic_mongo import AbstractRepository, PydanticObjectId
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()
  
uri = os.environ.get('uri')
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))


class UserSchema(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    orgId: PydanticObjectId
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    hashed_password: str
    role: str = Field(pattern="^(admin|analyst|reader)$")
    mfaEnabled: bool = False
    preferences: Dict[str, Any] = {}
    bio: Optional[str] = None
    date_joined_and_time_joined: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[str] = None

class UserRepository(AbstractRepository[UserSchema]):
    class Meta:
        database_name = 'tradingApp'
        collection_name = 'users'
    