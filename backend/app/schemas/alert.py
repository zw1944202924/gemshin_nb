from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AlertRuleBase(BaseModel):
    name: str
    rule_type: str
    condition: Dict[str, Any]
    notify_type: str = "feishu"
    is_enabled: bool = True


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    rule_type: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    notify_type: Optional[str] = None
    is_enabled: Optional[bool] = None


class AlertRuleResponse(AlertRuleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True