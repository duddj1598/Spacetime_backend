from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification_model import Notification
from app.schemas.notification_schema import NotificationListResponse

router = APIRouter(prefix="/api/notification", tags=["Notification"])

# ✅ 알림 목록 조회
@router.get("/list", response_model=NotificationListResponse)
def get_notifications(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    사용자의 알림 목록을 조회합니다.
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return {"status": 200, "notification": notifications}
