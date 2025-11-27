from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    nickname = Column(String, nullable=True)
    password = Column(String, nullable=False)

    # 🔥 Folder와 연결
    folders = relationship("Folder", back_populates="user")
