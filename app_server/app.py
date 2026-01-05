from fastapi import FastAPI, Body, HTTPException
from app_server.agent.claim_graph import claim_graph
import logging
import sys

# Logging Setup
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

app = FastAPI(title="Insurance Claim Agent")

@app.get("/")
def home():
    return {"status": "Claim Agent is Running", "port": 8002}

@app.post("/submit_claim")
async def submit_claim(claim: dict = Body(...)):
    """
    Trigger the Claims Processing Workflow
    """
    claim_id = claim.get("claim_id")
    if not claim_id:
        raise HTTPException(status_code=400, detail="claim_id is required")
        
    logging.info(f"Processing Claim ID: {claim_id}")
    
    # Initial State
    initial_state = {
        "claim_id": claim_id,
        "policy_id": claim.get("policy_id"),
        "fnol_data": claim.get("fnol_data", {}),
        "reasoning": []
    }
    
    try:
        # Run Graph
        final_state = await claim_graph.ainvoke(initial_state)
        
        return {
            "status": "completed",
            "claim_id": claim_id,
            "decision": final_state.get("decision"),
            "settlement_amount": final_state.get("settlement_amount"),
            "reasoning": final_state.get("reasoning"),
            "full_state": final_state
        }
    except Exception as e:
        logging.error(f"Error processing claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
