from django.test import TestCase

# Create your tests here.


# Test MongoDB connection
from pymongo import MongoClient

myclient = MongoClient("mongodb://localhost:27017/")

print(myclient.list_database_names())

dblist = myclient.list_database_names()
if "mydatabase" in dblist:
  print("The database exists.")
