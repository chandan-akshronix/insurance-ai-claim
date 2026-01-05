import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "insurance_ai")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
claims_collection = db["claims"]

from bson import ObjectId

def get_claim_by_id(claim_id: str):
    """
    Fetch a claim document from MongoDB by its claim_id, id, or _id.
    """
    try:
        # Build query: check claim_id, id, and _id (if valid ObjectId)
        query_conditions = [{"claim_id": claim_id}, {"id": claim_id}, {"_id": claim_id}]
        
        # Check if it's a valid ObjectId string
        if len(claim_id) == 24 and all(c in "0123456789abcdefABCDEF" for c in claim_id):
            query_conditions.append({"_id": ObjectId(claim_id)})
            
        query = {"$or": query_conditions}
        claim = claims_collection.find_one(query)
        
        if not claim:
            return None
            
        # Convert ObjectId to string for JSON serialization compatibility
        if "_id" in claim:
            claim["_id"] = str(claim["_id"])
            
        return claim
    except Exception as e:
        logging.error(f"Error fetching claim from MongoDB: {e}")
        return None
