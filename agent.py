import os
from typing import TypedDict, Optional, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# --- 1. Schemas & State Definition ---

class InventoryAlert(BaseModel):
    sku: str = Field(description="The SKU or product ID identified in the message")
    issue_type: str = Field(description="Type of issue: stockout, low_stock, or delay")
    reported_quantity: Optional[int] = Field(description="Reported current quantity, if stated")

class InventoryState(TypedDict):
    raw_input: str
    parsed_alert: Optional[InventoryAlert]
    current_stock: Optional[int]
    reorder_point: Optional[int]
    unit_cost: Optional[float]
    recommended_order_qty: Optional[int]
    total_cost: Optional[float]
    requires_approval: Optional[bool]
    status: str

# Mock Database Tool
MOCK_DB = {
    "SKU-101": {"stock": 12, "rop": 50, "unit_cost": 45.0, "eoq": 100},
    "SKU-202": {"stock": 200, "rop": 50, "unit_cost": 150.0, "eoq": 50},
    "SKU-303": {"stock": 5, "rop": 30, "unit_cost": 1200.0, "eoq": 20}, # High value
}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- 2. Agent Node Functions ---

def triage_agent(state: InventoryState) -> InventoryState:
    """Parses raw unstructured alerts into structured data."""
    structured_llm = llm.with_structured_output(InventoryAlert)
    prompt = f"Extract inventory exception details from this alert:\n\n{state['raw_input']}"
    parsed = structured_llm.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "parsed_alert": parsed,
        "status": "triaged"
    }

def data_retrieval_agent(state: InventoryState) -> InventoryState:
    """Fetches inventory metadata from the backend ERP database."""
    sku = state["parsed_alert"].sku if state["parsed_alert"] else None
    data = MOCK_DB.get(sku, {"stock": 0, "rop": 0, "unit_cost": 0.0, "eoq": 0})
    
    return {
        **state,
        "current_stock": data["stock"],
        "reorder_point": data["rop"],
        "unit_cost": data["unit_cost"],
        "recommended_order_qty": data["eoq"],
        "status": "data_fetched"
    }

def decision_agent(state: InventoryState) -> InventoryState:
    """Evaluates business rules, order thresholds, and approval paths."""
    qty = state["recommended_order_qty"] or 0
    unit_cost = state["unit_cost"] or 0.0
    total_cost = qty * unit_cost
    
    # Require human approval if order total exceeds $5,000
    requires_approval = total_cost > 5000.0
    
    return {
        **state,
        "total_cost": total_cost,
        "requires_approval": requires_approval,
        "status": "decision_made"
    }

def execution_agent(state: InventoryState) -> InventoryState:
    """Automates order placement for low-risk actions."""
    print(f"\n[SUCCESS] PO Drafted automatically for {state['parsed_alert'].sku}.")
    print(f"Details: {state['recommended_order_qty']} units @ ${state['unit_cost']}/unit. Total: ${state['total_cost']:.2f}")
    return {**state, "status": "completed"}

def human_approval_node(state: InventoryState) -> InventoryState:
    """Escalates high-value transactions to a human supervisor."""
    print(f"\n[ESCALATION] High-value order detected for {state['parsed_alert'].sku} (${state['total_cost']:.2f}).")
    print("Action Routing: Sent approval request to Operations Manager via Slack/Email.")
    return {**state, "status": "pending_human_approval"}

# --- 3. Routing Logic & Workflow Construction ---

def route_decision(state: InventoryState) -> Literal["execution", "human_approval"]:
    if state["requires_approval"]:
        return "human_approval"
    return "execution"

workflow = StateGraph(InventoryState)

workflow.add_node("triage", triage_agent)
workflow.add_node("retrieval", data_retrieval_agent)
workflow.add_node("decision", decision_agent)
workflow.add_node("execution", execution_agent)
workflow.add_node("human_approval", human_approval_node)

workflow.set_entry_point("triage")
workflow.add_edge("triage", "retrieval")
workflow.add_edge("retrieval", "decision")
workflow.add_conditional_edges("decision", route_decision)
workflow.add_edge("execution", END)
workflow.add_edge("human_approval", END)

app = workflow.compile()

# --- 4. Test Runs ---

if __name__ == "__main__":
    # Test 1: Standard Auto-Approval
    print("--- Running Test 1: Standard Reorder ---")
    app.invoke({"raw_input": "Warehouse A reports SKU-101 is down to 12 units. Need restock ASAP."})
    
    # Test 2: High-Value Order Escalation
    print("\n--- Running Test 2: High-Value Escalation ---")
    app.invoke({"raw_input": "Emergency alert: SKU-303 stock critical at 5 units!"})