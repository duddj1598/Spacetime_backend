from sqlalchemy import Column, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    nickname = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    birth = Column(String, nullable=True)
    agreedToTerms = Column(Boolean, default=False)
