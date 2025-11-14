from sqlalchemy import Column, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    nickname = Column(String, unique=True, nullable=False)
