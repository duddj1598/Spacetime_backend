from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    noti_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))  # 알림을 받는 유저
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

