from app_server.agent.state import ClaimAgentState
from typing import Dict, Any

def settlement_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Calculates final settlement and makes decision.
    """
    print("--- Settlement Node ---")
    
    fraud = state.get("fraud_risk", {})
    coverage = state.get("coverage_data", {})
    assessment = state.get("damage_assessment", {})
    
    if fraud.get("status") == "Investigate":
        return {
            "decision": "Investigate",
            "settlement_amount": 0,
            "reasoning": ["Claim flagged for fraud investigation."]
        }
        
    # Enforce Proof Verification for Auto-Approval
    proof_verified = state.get("proof_verified", False)
    doc_data = state.get("document_data", {})
    
    if not proof_verified:
        return {
            "decision": "Investigate",
            "settlement_amount": 0,
            "reasoning": ["Claim requires manual review: Proof of Claim could not be verified automatically from documents."]
        }

    # Optional: Confidence Threshold and Error Check
    low_confidence = False
    has_errors = False
    
    for unique_key, result in doc_data.get("results", {}).items():
        extraction = result.get("extraction", {})
        if "error" in extraction:
            has_errors = True
        if extraction.get("confidence", 1.0) < 0.6:
            low_confidence = True
            
    if low_confidence or has_errors:
         reason = "AI Extraction confidence for documents is too low." if low_confidence else "Some documents could not be read (Extraction Errors)."
         return {
            "decision": "Investigate",
            "settlement_amount": 0,
            "reasoning": [f"Claim requires manual review: {reason}"]
        }

    gross_amount = assessment.get("verified_amount", 0)
    deductible = coverage.get("deductible", 0)
    limit = coverage.get("coverage_limit", 0)
    
    # Calculate payout
    payable = min(gross_amount, limit) - deductible
    payable = max(payable, 0)
    
    res = {
        "settlement_amount": payable,
        "decision": "Approve",
        "reasoning": [
            f"✅ Settlement Approved. Gross: {gross_amount}, Deductible: {deductible}, Final Payout: {payable}"
        ]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="settlement_complete")

    return res
