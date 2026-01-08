import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env vars
load_dotenv(r"D:\final insurance project connection\langgraph claim process\.env")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("Error: MONGO_URI not found in .env")
    sys.exit(1)

try:
    client = MongoClient(MONGO_URI)
    db = client["insurance_ai"]
    claims_coll = db["claims"]
    
    print("--- Recent Claims in MongoDB ---")
    claims = list(claims_coll.find().sort("created_at", -1).limit(5))
    
    if not claims:
        print("No claims found.")
    else:
        for c in claims:
            print(f"ID: {c.get('_id')} | Status: {c.get('status')} | Policy: {c.get('policy_id') or c.get('policyNumber')}")
            
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
