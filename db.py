from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Used to secure mongo password
mongo_client = MongoClient(os.getenv("MONGO_URI"))

rhiunnearts_manager_db = mongo_client["rhiunnearts_manager_db"]

products_collection = rhiunnearts_manager_db["products"]

carts_collection = rhiunnearts_manager_db["carts"]

users_collection = rhiunnearts_manager_db["users"]