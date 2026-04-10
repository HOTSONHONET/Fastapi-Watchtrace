from pydantic import BaseModel
from typing import Any, Dict, List

class UserProfile(BaseModel):
    user_id: int
    name: str
    age: int
    tier: str

class Order(BaseModel):
    order_id: int
    amount: float
    category: str

class DashboardResponse(BaseModel):
    user: Dict[str, Any]
    orders: List[Dict[str, Any]]
    recommendations: List[str]
    analytics: Dict[str, Any]