from fastapi import FastAPI
from app.database import Base, engine
from app.models import user_model, friend_model, notification_model, folder_model, diary_model
from app.routers import auth_router, friend_router, notification_router, folder_router, diary_router

app = FastAPI(title="Spacetime API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(friend_router.router)
app.include_router(notification_router.router)
app.include_router(folder_router.router)
app.include_router(diary_router.router)
