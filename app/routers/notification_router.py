from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification_model import Notification
from app.schemas.notification_schema import NotificationListResponse, NotificationCreateRequest
from app.utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/notification", tags=["Notification"])

# ✅ 알림 목록 조회 (JWT 기반)
@router.get("/list", response_model=NotificationListResponse)
def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자의 알림 목록을 조회합니다. (JWT 기반)
    """
    print("현재 유저 정보:", current_user)  
    user_id = current_user["sub"]

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return {
        "status": 200,
        "notification": notifications
    }

@router.post("/create")
def create_notification(
    req: NotificationCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    JWT 기반: 현재 로그인한 유저에게 알림을 생성합니다.
    """
    user_id = current_user["sub"]

    new_notif = Notification(
        user_id=user_id,
        content=req.content
    )

    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    return {
        "status": 200,
        "message": "알림 생성 완료",
        "noti_id": new_notif.noti_id
    }