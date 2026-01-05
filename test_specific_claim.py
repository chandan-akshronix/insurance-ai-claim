
import requests
import json

def run_claim_test():
    claim_id = "695b47689b78d486cbc6752d"
    url = "http://localhost:8002/submit_claim"
    
    payload = {
        "claim_id": claim_id
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"--- Triggering Claim Agent for ID: {claim_id} ---")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            print("[SUCCESS] Agent response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[REJECT] Failed with status code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[ERROR] Error connecting to agent: {e}")
        print("💡 Make sure the agent is running: uvicorn app_server.app:app --reload --port 8002")

if __name__ == "__main__":
    run_claim_test()
