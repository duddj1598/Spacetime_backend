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

    diaries = relationship("Diary", back_populates="folder")
