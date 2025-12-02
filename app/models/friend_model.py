from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class FriendStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequest(Base):
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"))
    receiver_id = Column(String, ForeignKey("users.id"))
    status = Column(Enum(FriendStatus), default=FriendStatus.pending)
