from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    nickname = Column(String, nullable=True)
    password = Column(String, nullable=False)
    profile_image = Column(String, nullable=True)
    monthly_note = Column(String, nullable=True)  # 이번 달의 한 줄 기록

    folders = relationship("Folder", back_populates="user")