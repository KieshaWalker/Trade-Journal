import os 
from django.contrib.auth.models import User
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic_mongo import AbstractRepository, PydanticObjectId
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from dotenv import load_dotenv
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
    hashed_password: str
    role: str = Field(pattern="^(admin|analyst|reader)$")
    mfaEnabled: bool = False
    preferences: Dict[str, Any] = {}

class UserRepository(AbstractRepository[UserSchema]):
    class Meta:
        database_name = 'tradingApp'
        collection_name = 'users'git