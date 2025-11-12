from pydantic import BaseModel
from datetime import datetime
from typing import List

class NotificationResponseItem(BaseModel):
    noti_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationListResponse(BaseModel):
    status: int
    notification: List[NotificationResponseItem]
