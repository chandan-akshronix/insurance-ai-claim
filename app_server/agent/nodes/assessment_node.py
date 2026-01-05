from app_server.agent.state import ClaimAgentState
from typing import Dict, Any

def assessment_node(state: ClaimAgentState) -> Dict[str, Any]:
    """
    Evaluates damage and repair costs.
    """
    print("--- Assessment Node ---")
    
    fnol_data = state.get("fnol_data", {})
    claim_type = fnol_data.get("claim_type", "General")
    
    # Prioritize Document Data for Assessment
    doc_results = state.get("document_data", {}).get("results", {})
    ext_amount = 0.0
    for filename, result in doc_results.items():
        ext_data = result.get("extraction", {}).get("extracted_data", {})
        # Look for bill amounts or total amounts in documents
        amt_str = ext_data.get("total_amount") or ext_data.get("bill_amount") or ext_data.get("amount")
        if amt_str:
            from app_server.utils.helpers import parse_currency
            ext_amount = max(ext_amount, parse_currency(amt_str))

    # Life insurance is usually a fixed payout (Sum Assured)
    if claim_type == "life":
        print("Life Claim: Applying Sum Assured payout logic.")
        # In a real system, fetch 'sum_assured' from policy. 
        # Here we use 1,000,000 as a default.
        assessed_amount = 1000000.0
        notes = "Full Sum Assured approved for life claim."
    elif ext_amount > 0:
        print(f"Document-Driven Assessment: Using extracted amount {ext_amount}")
        assessed_amount = ext_amount
        notes = f"Amount verified from uploaded documents: {ext_amount}"
    else:
        estimated = fnol_data.get("estimated_amount", 10000)
        assessed_amount = estimated * 0.9 # 10% depreciation
        notes = "Applied standard 10% depreciation on parts."
    
    res = {
        "damage_assessment": {
            "verified_amount": assessed_amount,
            "notes": notes
        },
        "reasoning": [f"Assessed amount: {assessed_amount}"]
    }

    # Sync to backend
    from app_server.utils.sync import sync_claim_state_to_backend
    sync_claim_state_to_backend({**state, **res}, current_step="damage_assessment")

    return res
