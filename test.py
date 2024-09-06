from pymongo import MongoClient
from dotenv import load_dotenv

client = MongoClient(MONGODB_URI)
db = client.dbsparta

doc = {
    'name': '영수',
    'age': 24
}

db.users.insert_one(doc)