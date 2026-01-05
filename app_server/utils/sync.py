import os
import requests
import json
import logging
from datetime import date, datetime
from app_server.utils.claim_ui_mapper import map_claim_state_to_timeline

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

def sync_claim_state_to_backend(state: dict, current_step: str, status: str = "processing"):
    """
    Syncs the current ClaimAgentState to the Backend API for display in Admin Panel.
    """
    claim_id = state.get("claim_id")
    if not claim_id:
        logging.warning("No claim_id found in state, skipping sync.")
        return

    # Map decision to backend expected status
    # investigate -> manual_review, reject -> rejected, approve -> approved
    backend_status = status
    if state.get("decision"):
        decision = state.get("decision").lower()
        if decision == "investigate":
            backend_status = "manual_review"
        elif decision == "reject":
            backend_status = "rejected"
        elif decision == "approve":
            backend_status = "approved"

    # Fetch existing step history to preserve manual completions
    existing_step_history = None
    try:
        response = requests.get(f"{BACKEND_URL}/agent/application/{claim_id}", timeout=2)
        if response.status_code == 200:
            existing_data = response.json()
            existing_step_history = existing_data.get("stepHistory")
    except Exception as e:
        logging.debug(f"Could not fetch existing step history: {e}")
    
    # Map state to UI step history
    step_history = map_claim_state_to_timeline(state, existing_step_history)
    
    # Prepare payload matching schemas.ApplicationProcessCreate
    payload = {
        "applicationId": claim_id,
        "status": backend_status,
        "currentStep": current_step,
        "agentData": state, 
        "stepHistory": step_history,
        "startTime": date.today().isoformat()
    }
    
    try:
        # Handle potential non-serializable objects (like datetime)
        json_str = json.dumps(payload, cls=DateTimeEncoder)
        payload_dict = json.loads(json_str) 
        
        response = requests.post(f"{BACKEND_URL}/agent/sync", json=payload_dict, timeout=5)
        if response.status_code >= 400:
             logging.error(f"Backend sync failed: {response.status_code} - {response.text}")
        else:
             logging.info(f"✅ Synced claim state to backend for {claim_id}. Step: {current_step}")
    except Exception as e:
        logging.error(f"❌ Error syncing claim to backend: {e}")
