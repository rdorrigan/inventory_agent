import pytest
from src.agent.graph import build_inventory_graph

@pytest.fixture
def agent_app():
    return build_inventory_graph()

def test_high_value_escalation_path(agent_app):
    state = {
        "raw_input": "Critical low stock on SKU-303! Down to 5 units.",
        "parsed_alert": None,
        "errors": []
    }
    result = agent_app.invoke(state)
    
    assert result["parsed_alert"].sku == "SKU-303"
    assert result["requires_approval"] is True
    assert result["status"] == "pending_human_approval"