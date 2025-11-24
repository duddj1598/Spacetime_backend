from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserResponse, UserEdit

router = APIRouter(prefix="/api/user", tags=["User"])


# ===========================================
# ✔ 내 정보 조회
# GET /api/user/me
# ===========================================
@router.get("/me")
def get_my_info(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    data = UserResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        nickname=user.nickname,
        profile_image=user.profile_image,
    )

    return {
        "status": 200,
        "message": "회원 정보 조회가 완료되었습니다.",
        "data": [data],
    }


# ===========================================
# ✔ 내 정보 수정
# PUT /api/user/edit
# ===========================================
@router.put("/edit")
def edit_my_info(edit_data: UserEdit, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == edit_data.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 변경 가능한 필드만 업데이트
    if edit_data.profile_image is not None:
        user.profile_image = edit_data.profile_image

    if edit_data.nickname is not None:
        user.nickname = edit_data.nickname

    if edit_data.name is not None:
        user.name = edit_data.name

    db.commit()
    db.refresh(user)

    data = UserResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        nickname=user.nickname,
        profile_image=user.profile_image,
    )

    return {
        "status": 200,
        "message": "회원 정보 수정이 완료되었습니다.",
        "data": [data],
    }
