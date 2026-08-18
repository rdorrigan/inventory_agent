from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.graph import build_inventory_graph

app = FastAPI(title="Inventory Agentic Workflow API", version="1.0.0")
workflow_app = build_inventory_graph()

class AlertRequest(BaseModel):
    alert_text: str

class AlertResponse(BaseModel):
    sku: str
    total_cost: float
    requires_approval: bool
    status: str

@app.post("/api/v1/triage", response_model=AlertResponse)
async def process_alert(request: AlertRequest):
    initial_state = {
        "raw_input": request.alert_text,
        "parsed_alert": None,
        "current_stock": None,
        "reorder_point": None,
        "unit_cost": None,
        "recommended_order_qty": None,
        "total_cost": None,
        "requires_approval": None,
        "status": "initiated",
        "errors": []
    }
    
    result = workflow_app.invoke(initial_state)
    
    if not result.get("parsed_alert"):
        raise HTTPException(status_code=422, detail="Failed to parse valid SKU from request.")
        
    return AlertResponse(
        sku=result["parsed_alert"].sku,
        total_cost=result.get("total_cost", 0.0),
        requires_approval=result.get("requires_approval", False),
        status=result.get("status", "unknown")
    )