from fastapi import FastAPI
from app.database import Base, engine
from app.models import user_model
from app.routers import auth_router

app = FastAPI(title="Spacetime API")

# 🚀 앱 시작 시 DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(auth_router.router)
