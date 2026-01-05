
from app_server.agent.state import ClaimAgentState
from app_server.utils.postgres_utils import fetch_policy_by_number
from typing import Dict, Any

def policy_verification_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Verifies policy existence and status in PostgreSQL.
    """
    print("--- Policy Verification Node (SQL) ---")
    
    fnol_data = state.get("fnol_data", {})
    policy_number = fnol_data.get("policyNumber")
    
    if not policy_number:
        return {
            "decision": "Reject",
            "reasoning": ["Policy verification failed: Missing policyNumber in claim data."]
        }
        
    print(f"🔍 Fetching policy details for: {policy_number}")
    policy_data = fetch_policy_by_number(policy_number)
    
    if not policy_data:
        return {
            "decision": "Reject",
            "reasoning": [f"Policy verification failed: Policy {policy_number} not found in SQL database."]
        }
        
    # Validation: Check if policy is active
    status = policy_data.get("status")
    print(f"✅ Policy found in SQL. Status: {status}")
    
    if status != "Active":
        return {
            "policy_sql_data": policy_data,
            "decision": "Reject",
            "reasoning": [f"Policy verification failed: Policy {policy_number} is in '{status}' status (must be Active)."]
        }

    res = {
        "policy_sql_data": policy_data,
        "reasoning": [f"SQL Policy Verified: Found active policy {policy_number}."]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="policy_verification")

    return res
