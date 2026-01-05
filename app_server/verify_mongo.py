import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_server.utils.mongodb_utils import get_claim_by_id, claims_collection, client, DB_NAME
import json

def verify_connection():
    print("--- Debugging 'claims' collection ---")
    try:
        db = client["insurance_ai"]
        coll = db["claims"]
        count = coll.count_documents({})
        print(f"Total documents in 'claims': {count}")
        
        docs = list(coll.find())
        for i, doc in enumerate(docs):
            print(f"\n--- Document {i+1} ---")
            print(json.dumps(doc, indent=2, default=str))
            
            # Check if it matches the target_id
            target_id = "69522904d6e9c639ac1c7db1"
            if str(doc.get("_id")) == target_id or doc.get("id") == target_id or doc.get("claim_id") == target_id:
                print(f"MATCH FOUND for {target_id}!")
            
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_connection()
