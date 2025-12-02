from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, friend_router, notification_router, folder_router, diary_router, user_router

app = FastAPI(title="Spacetime API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)
app.include_router(friend_router.router)
app.include_router(notification_router.router)
app.include_router(folder_router.router)
app.include_router(diary_router.router)
app.include_router(user_router.router)
