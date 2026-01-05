from typing import TypedDict, List, Optional, Any, Dict
import operator
from typing import Annotated

class ClaimAgentState(TypedDict):
    # Inputs
    claim_id: str
    policy_id: str
    
    # Workflow Data
    fnol_data: Dict[str, Any]  # First Notice of Loss details
    coverage_data: Dict[str, Any] # Policy coverage verification
    fraud_risk: Dict[str, Any]    # Fraud check results
    damage_assessment: Dict[str, Any] # Damage evaluation
    
    # Decisions
    settlement_amount: float
    decision: str  # "Approve", "Reject", "Investigate"
    reasoning: Annotated[List[str], operator.add]
    
    # Checkpointing
    current_step: str
    
    # Document Extraction Data
    document_data: Dict[str, Any] # results from document_reader_node
    proof_verified: bool  # Whether document matches user input
    policy_sql_data: Dict[str, Any] # Data fetched from PostgreSQL Policy table
