import os
from django.test import TestCase


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
  

uri = os.environ.get('uri')
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    database = client.get_database("sample_mflix")
    movies = database.get_collection("movies")
    # Query for a movie that has the title 'Back to the Future'
    query = { "title": "Back to the Future" }
    movie = movies.find_one(query)
    print(movie)
    
    # Access the database named "mydatabase".
    # If "mydatabase" does not exist, MongoDB will create it when content is added.
    mydb = client["mydatabase"]

    # Access a collection named "mycollection" within "mydatabase".
    # If "mycollection" does not exist, MongoDB will create it.
    mycol = mydb["mycollection"]

    # Insert a document into the collection. This action will create both the collection
    # and the database if they don't already exist.
    mydocument = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydocument)
    print(f"Document inserted with ID: {x.inserted_id}")

    print(client.list_database_names())
    client.close()
except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)