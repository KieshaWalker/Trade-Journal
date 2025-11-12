from django.test import TestCase


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://llcwalkerk_db_user:OuQwUNsGSAgwgsxB@student-cluster.k12a4iv.mongodb.net/tradingApp?appName=student-cluster"
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
    client.close()
except Exception as e:
    raise Exception("Unable to find the document due to the following error: ", e)

