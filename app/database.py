from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite DB 생성 (파일명: spacetime.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./spacetime.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 의존성 주입용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
