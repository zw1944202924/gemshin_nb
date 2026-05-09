from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class NotificationCreate(BaseModel):
    title: str
    content: str
    notify_type: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    notify_type: str
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True


class UserNotifyConfig(BaseModel):
    feishu_webhook: Optional[str] = None
    email: Optional[str] = None


class NotifySendRequest(BaseModel):
    notify_type: str
    title: str
    content: str
    receivers: Optional[List[str]] = None