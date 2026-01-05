from app_server.agent.state import ClaimAgentState
from typing import Dict, Any
import random

def fraud_check_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Analyzes claim for fraud markers.
    """
    print("--- Fraud Check Node ---")
    
    fnol_data = state.get("fnol_data", {})
    claim_amount = fnol_data.get("estimated_amount", 0)
    
    # Mock Fraud Logic
    risk_score = 10
    flags = []
    
    # High value claims are higher risk
    # Use verified amount from assessment if available, otherwise fallback to estimate
    assessed_amount = state.get("damage_assessment", {}).get("verified_amount", 0)
    current_amount = assessed_amount if assessed_amount > 0 else fnol_data.get("estimated_amount", 0)
    
    if current_amount > 100000:
        risk_score += 40
        flags.append(f"High Value Claim ({current_amount})")
        
    # Random check (deterministic for 'FRAUD' in ID)
    if "FRAUD" in state.get("claim_id", ""):
        risk_score = 95
        flags.append("Suspicious Activity Pattern")

    # Document Extraction Intelligence
    doc_results = state.get("document_data", {}).get("results", {})
    for filename, result in doc_results.items():
        extraction = result.get("extraction", {})
        if "error" in extraction:
            flags.append(f"Incomplete Document Data ({filename})")
            risk_score += 5
        elif extraction.get("confidence", 1.0) < 0.5:
            flags.append(f"Low Confidence Extraction ({filename})")
            risk_score += 10
        
    fraud_data = {
        "risk_score": risk_score,
        "flags": flags,
        "status": "Investigate" if risk_score > 70 else "Clear"
    }
    
    res = {
        "fraud_risk": fraud_data,
        "reasoning": [f"Fraud Risk Score: {risk_score} ({fraud_data['status']})"]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="fraud_check")

    return res
