from app_server.agent.state import ClaimAgentState
from app_server.utils.mongodb_utils import get_claim_by_id
from typing import Dict, Any
import datetime
import logging

def fnol_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    First Notice of Loss (FNOL) Node.
    Ingests claim details and performs basic validation.
    If fnol_data is missing, it attempts to fetch it from MongoDB using claim_id.
    """
    print("--- FNOL Node ---")
    
    claim_id = state.get("claim_id")
    fnol_data = state.get("fnol_data", {})
    
    # If data is missing, fetch from MongoDB
    if not fnol_data and claim_id:
        print(f"FNOL data missing for {claim_id}. Fetching from MongoDB...")
        fetched_data = get_claim_by_id(claim_id)
        if fetched_data:
            print(f"Successfully fetched data for claim {claim_id}")
            fnol_data = fetched_data
        else:
            return {"decision": "Reject", "reasoning": [f"Could not find claim details for ID: {claim_id}"]}
    
    # Comprehensive Schema Validation
    required_global = ["user_id", "policy_id", "claim_type", "status"]
    missing_fields = []
    
    # Check for global fields (support both camelCase and snake_case for user/policy)
    for field in required_global:
        val = fnol_data.get(field)
        if field == "user_id" and not val:
            val = fnol_data.get("userId")
        if field == "policy_id" and not val:
            val = fnol_data.get("policyId")
            
        if not val:
            missing_fields.append(field)
            
    claim_type = fnol_data.get("claim_type", "General")
    
    # Life Insurance Specific Validation
    if claim_type == "life":
        death_details = fnol_data.get("death_details", {})
        if not death_details:
            missing_fields.append("death_details")
        else:
            if not death_details.get("date_of_death"): missing_fields.append("death_details.date_of_death")
            if not death_details.get("cause_of_death"): missing_fields.append("death_details.cause_of_death")
        
        claimant_info = fnol_data.get("claimant_info", {})
        if not claimant_info or not claimant_info.get("name"):
            missing_fields.append("claimant_info.name")
            
    elif claim_type == "car":
        accident_details = fnol_data.get("accident_details", {})
        if not accident_details:
            missing_fields.append("accident_details")
        else:
            if not accident_details.get("accident_type"): missing_fields.append("accident_details.accident_type")
            
    elif claim_type == "health":
        hosp_details = fnol_data.get("hospitalization_details", {})
        if not hosp_details:
            missing_fields.append("hospitalization_details")
        else:
            if not hosp_details.get("admission_date"): missing_fields.append("hospitalization_details.admission_date")

    if missing_fields:
        return {
            "decision": "Reject", 
            "reasoning": [f"Missing required fields in schema: {', '.join(missing_fields)}"]
        }
        
    # Extract incident date for general processing
    incident_date = None
    if claim_type == "life":
        incident_date = fnol_data.get("death_details", {}).get("date_of_death")
    else:
        # Check incident_details first
        incident_date = fnol_data.get("incident_details", {}).get("incident_date")
        # Fallback to type-specific fields
        if not incident_date:
            if claim_type == "car": incident_date = fnol_data.get("accident_details", {}).get("accident_date")
            elif claim_type == "health": incident_date = fnol_data.get("hospitalization_details", {}).get("admission_date")

    if not incident_date:
        return {"decision": "Reject", "reasoning": ["Could not extract incident date from provided details"]}
    
    # Document Completeness Validation
    documents = fnol_data.get("documents", [])
    provided_categories = {doc.get("category") for doc in documents if doc.get("category")}
    
    mandatory_docs = {
        "life": ["death-certificate", "bank-details"],
        "car": ["claim-form", "rc-copy", "driving-license", "damage-photos"],
        "health": ["claim-form", "hospital-bills", "discharge-summary"]
    }
    
    missing_docs = [doc for doc in mandatory_docs.get(claim_type, []) if doc not in provided_categories]
    
    if missing_docs:
        return {
            "decision": "Reject",
            "reasoning": [f"Missing mandatory documents for {claim_type} claim: {', '.join(missing_docs)}"]
        }

    print(f"FNOL Schema & Documents Validated for {claim_type} Claim: {claim_id}")
    
    res = {
        "fnol_data": fnol_data,
        "current_step": "fnol_complete",
        "reasoning": [f"Full schema for {claim_type} claim validated successfully. All required fields present."]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="fnol_validation")
    
    return res
