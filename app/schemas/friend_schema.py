# app/schemas/friend_schema.py
from pydantic import BaseModel
from typing import List, Optional

class FriendListResponse(BaseModel):
    status: int
    friends: list

class FriendRequestCreate(BaseModel):
    target_nickname: str

class FriendAcceptRequest(BaseModel):
    action: str  # "accept" or "reject"
