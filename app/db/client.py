from pymongo import AsyncMongoClient

mongo_client: AsyncMongoClient = AsyncMongoClient(
    "mongodb://admin:password@mongo:27017")
