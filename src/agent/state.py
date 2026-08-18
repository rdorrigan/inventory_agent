from typing import TypedDict, Optional, List
from pydantic import BaseModel, Field

class InventoryAlert(BaseModel):
    sku: str = Field(description="The target SKU identifier extracted from the alert.")
    issue_type: str = Field(description="Type of alert: stockout, low_stock, delay")
    reported_quantity: Optional[int] = Field(default=None, description="Current stock quantity if stated.")

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
    errors: List[str]