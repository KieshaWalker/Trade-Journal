from typing import Optional, List, Dict, Any, NewType
from datetime import datetime, date, timezone
from pydantic import BaseModel, Field, EmailStr
import os
from django.db import models
from django.contrib.auth.models import User
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic_mongo import AbstractRepository, PydanticObjectId

# Lazy MongoClient getter — don't import or connect at import time
_mongo_client = None
_mongo_client_class = None

def get_mongo_client(uri=None):
    global _mongo_client, _mongo_client_class
    if _mongo_client is None:
        if _mongo_client_class is None:
            try:
                from pymongo import MongoClient as MC
                _mongo_client_class = MC
            except ImportError:
                _mongo_client_class = None
                return None
        if _mongo_client_class is not None:
            import os
            uri = uri or os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
            _mongo_client = _mongo_client_class(uri)
    return _mongo_client

class Trade(models.Model):
    pass
