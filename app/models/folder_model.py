from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Folder(Base):
    __tablename__ = "folders"

    folder_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    main_folder_img = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)

    # 🔥 이것이 반드시 필요함 (User 모델과 연결)
    user = relationship("User", back_populates="folders")

    # 이미 존재하는 Diary 관계
    diaries = relationship("Diary", back_populates="folder")
