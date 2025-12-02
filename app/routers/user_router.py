from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.models.folder_model import Folder
from app.schemas.user_schema import UserResponse, UserEdit, MonthlyNoteUpdate
from app.utils.jwt_handler import get_current_user

router = APIRouter(prefix="/api/user", tags=["User"])


# ===========================================
# ✔ 마이페이지 정보 조회 (JWT만으로 처리)
# GET /api/user/me
# ===========================================
@router.get("/me")
def get_my_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰만으로 마이페이지 정보를 조회합니다.
    - 닉네임
    - 프로필 이미지
    - 친구 수
    - 이번 달의 한 줄 기록
    """
    # 친구 수 계산
    from app.models.friend_model import FriendRequest, FriendStatus
    
    sent_friends = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.status == FriendStatus.accepted
    ).count()
    
    received_friends = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendStatus.accepted
    ).count()
    
    friend_count = sent_friends + received_friends

    # ⭐ 프론트엔드 호환을 위해 data를 객체로 반환 (배열 아님)
    return {
        "status": 200,
        "message": "마이페이지 조회가 완료되었습니다.",
        "data": {
            "user_id": current_user.id,
            "nickname": current_user.nickname,
            "profile_image": current_user.profile_image,
            "friend_count": friend_count,
            "monthly_note": current_user.monthly_note
        }
    }


# ===========================================
# ✔ 이번 달의 한 줄 기록 수정 (JWT만으로 처리)
# PUT /api/user/monthly-note
# ===========================================
@router.put("/monthly-note")
def update_monthly_note(
    note_data: MonthlyNoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰을 사용하여 이번 달의 한 줄 기록을 업데이트합니다.
    """
    # 글자 수 제한 (100자)
    if len(note_data.monthly_note) > 100:
        raise HTTPException(status_code=400, detail="한 줄 기록은 100자를 초과할 수 없습니다.")
    
    current_user.monthly_note = note_data.monthly_note
    db.commit()
    db.refresh(current_user)

    return {
        "status": 200,
        "message": "이번 달의 한 줄 기록이 수정되었습니다.",
        "data": {
            "monthly_note": current_user.monthly_note
        }
    }


# ===========================================
# ✔ 프로필 정보 수정 (JWT만으로 처리)
# PUT /api/user/edit
# ===========================================
@router.put("/edit")
def edit_my_info(
    edit_data: UserEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰을 사용하여 프로필 정보를 수정합니다.
    """
    # 닉네임 중복 체크 (자신의 닉네임이 아닌 경우)
    if edit_data.nickname and edit_data.nickname != current_user.nickname:
        existing_user = db.query(User).filter(
            User.nickname == edit_data.nickname,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")

    # 변경 가능한 필드만 업데이트
    if edit_data.profile_image is not None:
        current_user.profile_image = edit_data.profile_image

    if edit_data.nickname is not None:
        current_user.nickname = edit_data.nickname

    db.commit()
    db.refresh(current_user)

    return {
        "status": 200,
        "message": "회원 정보 수정이 완료되었습니다.",
        "data": {
            "user_id": current_user.id,
            "nickname": current_user.nickname,
            "profile_image": current_user.profile_image,
        }
    }


# ===========================================
# ✔ 나의 기록 모아보기 (JWT만으로 처리)
# GET /api/user/my-diaries
# ===========================================
# user_router.py의 get_my_folders 함수 수정

@router.get("/my-diaries")
def get_my_folders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰을 사용하여 내 모든 폴더와 일기를 조회합니다.
    마이페이지의 '나의 기록 모아보기' 섹션용입니다.
    """
    from app.models.diary_model import Diary
    
    # 내 모든 폴더 조회
    my_folders = db.query(Folder).filter(Folder.user_id == current_user.id).all()
    
    result = []
    for folder in my_folders:
        # 각 폴더의 일기들 조회
        diaries = db.query(Diary).filter(Diary.folder_id == folder.folder_id).all()
        
        diary_list = []
        for diary in diaries:
            main_photo = diary.photos[0] if diary.photos else None
            diary_list.append({
                "diary_id": diary.diary_id,
                "title": diary.title,
                "main_photo": main_photo,
                "location": diary.location
            })
        
        # ⭐️ is_public, main_folder_img 추가
        result.append({
            "folder_id": folder.folder_id,
            "title": folder.title,  # ⭐️ folder_title → title로 변경
            "is_public": folder.is_public,  # ⭐️ 추가
            "main_folder_img": folder.main_folder_img,  # ⭐️ 추가
            "diaries": diary_list
            # ❌ created_at 제거! (Folder 모델에 없음)
        })
    
    return {
        "status": 200,
        "message": "나의 기록 조회가 완료되었습니다.",
        "data": result
    }