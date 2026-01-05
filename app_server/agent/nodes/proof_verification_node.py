
from typing import Dict, Any
from app_server.agent.state import ClaimAgentState
from datetime import datetime

def proof_verification_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Compares user-provided fnol_data with AI-extracted document_data.
    Acts as the 'Proof of Claim' verification engine.
    """
    print("--- Proof Verification Node ---")
    
    fnol_data = state.get("fnol_data", {})
    doc_results = state.get("document_data", {}).get("results", {})
    
    verification_flags = []
    proof_verified = True
    reasoning = []

    # 1. Check for missing document data
    if not doc_results or state.get("document_data", {}).get("status") == "skipped":
        reasoning.append("Warning: No document data available for proof verification.")
        return {"proof_verified": False, "reasoning": reasoning}

    # 2. Extract key fields for comparison
    user_name = fnol_data.get("claimant_info", {}).get("name", "").lower()
    user_date = fnol_data.get("death_details", {}).get("date_of_death") or fnol_data.get("incident_details", {}).get("incident_date")

    # 3. Cross-reference with results
    successful_extractions = 0
    extraction_errors = 0

    for unique_key, result in doc_results.items():
        extraction = result.get("extraction", {})
        if "error" in extraction:
            extraction_errors += 1
            verification_flags.append(f"Extraction Error in {unique_key}: {extraction.get('error')}")
            continue
            
        successful_extractions += 1
        ext_data = extraction.get("extracted_data", {})
        ext_name = (ext_data.get("name") or ext_data.get("name_of_deceased") or "").lower()
        ext_date = ext_data.get("date_of_death") or ext_data.get("date_of_admission") or ext_data.get("date")
        
        # Name Match (Fuzzy-ish)
        if ext_name and user_name:
            if user_name not in ext_name and ext_name not in user_name:
                verification_flags.append(f"Name Mismatch in {unique_key}: User says '{user_name}', Doc says '{ext_name}'")
                proof_verified = False

        # Date Match
        if ext_date and user_date:
            if str(user_date) not in str(ext_date) and str(ext_date) not in str(user_date):
                verification_flags.append(f"Date Mismatch in {unique_key}: User says '{user_date}', Doc says '{ext_date}'")
                proof_verified = False

    # Force failure if no successful extractions or if there were errors
    if successful_extractions == 0 or extraction_errors > 0:
        proof_verified = False
        if extraction_errors > 0:
            reasoning.append(f"🚫 Proof Verification Failed: {extraction_errors} document(s) could not be read.")
        else:
            reasoning.append("🚫 Proof Verification Failed: No documents were successfully processed.")

    decision = "Investigate" if not proof_verified else state.get("decision", "Approve")

    res = {
        "proof_verified": proof_verified,
        "decision": decision,
        "reasoning": reasoning + verification_flags
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="proof_verification")

    return res
