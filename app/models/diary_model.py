from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Diary(Base):
    __tablename__ = "diaries"

    diary_id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.folder_id"))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    photos = Column(JSON, nullable=True)
    theme = Column(String, nullable=True)
    location = Column(JSON, nullable=True)

    folder = relationship("Folder", back_populates="diaries")
