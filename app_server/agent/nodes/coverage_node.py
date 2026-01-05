from app_server.agent.state import ClaimAgentState
from typing import Dict, Any

def coverage_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Verifies if the policy covers the reported incident.
    """
    print("--- Coverage Verification Node ---")
    
    policy_id = state.get("policy_id")
    fnol_data = state.get("fnol_data", {})
    claim_type = fnol_data.get("claim_type", "General")
    
    # Use Data from SQL Verification
    sql_data = state.get("policy_sql_data", {})
    
    if sql_data:
        print(f"Using SQL data for coverage verification: {policy_id}")
        is_covered = True
        # Extract coverage limit from SQL (using 'coverage' column found in schema)
        coverage_limit = sql_data.get("coverage", 1000000)
        policy_status = sql_data.get("status")
        
        if policy_status != "Active":
            is_covered = False
    else:
        # Fallback to Mock if SQL data is missing
        print(f"⚠️ SQL data missing, falling back to mock for {policy_id}")
        is_covered = True
        coverage_limit = 500000 
        if claim_type == "life":
            coverage_limit = 1000000
    
    coverage_data = {
        "is_active": True,
        "covers_incident_type": is_covered,
        "deductible": 0 if claim_type == "life" else 5000,
        "coverage_limit": float(coverage_limit)
    }
    
    if not is_covered:
        return {
            "coverage_data": coverage_data,
            "decision": "Reject", 
            "reasoning": [f"Policy {policy_id} does not cover {claim_type} claim status."]
        }
    
    res = {
        "coverage_data": coverage_data,
        "reasoning": [f"Policy covers {claim_type} insurance up to {coverage_limit}"]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="coverage_analysis")

    return res
