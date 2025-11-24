from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    password = Column(String, nullable=False)

    # 🔥 Folder와 연결
    folders = relationship("Folder", back_populates="user")
