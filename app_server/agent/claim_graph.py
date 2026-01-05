from langgraph.graph import StateGraph, END
from app_server.agent.state import ClaimAgentState

# Import Nodes
from app_server.agent.nodes.fnol_node import fnol_node
from app_server.agent.nodes.policy_verification_node import policy_verification_node
from app_server.agent.nodes.document_reader_node import document_reader_node
from app_server.agent.nodes.proof_verification_node import proof_verification_node
from app_server.agent.nodes.coverage_node import coverage_node
from app_server.agent.nodes.fraud_check_node import fraud_check_node
from app_server.agent.nodes.assessment_node import assessment_node
from app_server.agent.nodes.settlement_node import settlement_node

# Graph Construction
workflow = StateGraph(ClaimAgentState)

# Add Nodes
workflow.add_node("fnol", fnol_node)
workflow.add_node("policy_verification", policy_verification_node)
workflow.add_node("document_reader", document_reader_node)
workflow.add_node("proof_verification", proof_verification_node)
workflow.add_node("coverage", coverage_node)
workflow.add_node("fraud_check", fraud_check_node)
workflow.add_node("assessment", assessment_node)
workflow.add_node("settlement", settlement_node)

# Set Entry Point
workflow.set_entry_point("fnol")

# Define Edges

# 1. FNOL -> Policy Verification
def check_fnol(state: ClaimAgentState):
    if state.get("decision") == "Reject":
        return END
    return "policy_verification"

workflow.add_conditional_edges("fnol", check_fnol, {"policy_verification": "policy_verification", END: END})

# 1b. Policy Verification -> Document Reader
def check_policy_sql(state: ClaimAgentState):
    if state.get("decision") == "Reject":
        return END
    return "document_reader"

workflow.add_conditional_edges("policy_verification", check_policy_sql, {"document_reader": "document_reader", END: END})

# 2. Document Reader -> Proof Verification
workflow.add_edge("document_reader", "proof_verification")

# 3. Proof Verification -> Coverage
workflow.add_edge("proof_verification", "coverage")

# 4. Coverage -> Fraud Check
def check_coverage(state: ClaimAgentState):
    if state.get("decision") == "Reject":
        return END
    return "fraud_check"

workflow.add_conditional_edges("coverage", check_coverage, {"fraud_check": "fraud_check", END: END})

# 3. Fraud Check -> (Assessment / Settlement)
def check_fraud(state: ClaimAgentState):
    fraud = state.get("fraud_risk", {})
    # Go to settlement immediately if fraud is suspected OR if someone else flagged for investigation
    if fraud.get("status") == "Investigate" or state.get("decision") == "Investigate":
        # Skip assessment, go straight to settlement
        return "settlement"
    return "assessment"

workflow.add_conditional_edges("fraud_check", check_fraud, {"settlement": "settlement", "assessment": "assessment"})

# 4. Assessment -> Settlement
workflow.add_edge("assessment", "settlement")

# 5. Settlement -> END
workflow.add_edge("settlement", END)

# Compile
claim_graph = workflow.compile()
