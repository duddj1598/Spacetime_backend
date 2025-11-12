# app/routers/friend_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.schemas.friend_schema import FriendRequestCreate, FriendAcceptRequest

router = APIRouter(prefix="/api/friend", tags=["Friend"])

# ✅ 1. 친구 목록 조회
@router.get("/list")
def get_friend_list(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    user_id를 기반으로 친구 목록을 조회합니다.
    """
    # 친구 관계 (양방향 accepted 상태)
    sent_friends = (
        db.query(FriendRequest)
        .filter(FriendRequest.sender_id == user_id, FriendRequest.status == FriendStatus.accepted)
        .all()
    )
    received_friends = (
        db.query(FriendRequest)
        .filter(FriendRequest.receiver_id == user_id, FriendRequest.status == FriendStatus.accepted)
        .all()
    )

    friend_list = []
    for f in sent_friends:
        friend_user = db.query(User).filter(User.id == f.receiver_id).first()
        if friend_user:
            friend_list.append({"nickname": friend_user.nickname, "friend_id": friend_user.id})

    for f in received_friends:
        friend_user = db.query(User).filter(User.id == f.sender_id).first()
        if friend_user:
            friend_list.append({"nickname": friend_user.nickname, "friend_id": friend_user.id})

    return {"status": 200, "friends": friend_list}


# ✅ 2. 친구 추가 요청
@router.post("/request")
def send_friend_request(request: FriendRequestCreate, sender_id: str = Query(...), db: Session = Depends(get_db)):
    """
    닉네임으로 친구 요청을 전송합니다.
    """
    target_user = db.query(User).filter(User.nickname == request.target_nickname).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="해당 닉네임의 사용자를 찾을 수 없습니다.")

    # 이미 친구 요청 or 친구 상태 확인
    existing = (
        db.query(FriendRequest)
        .filter(
            ((FriendRequest.sender_id == sender_id) & (FriendRequest.receiver_id == target_user.id))
            | ((FriendRequest.sender_id == target_user.id) & (FriendRequest.receiver_id == sender_id))
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="이미 친구 요청이 존재합니다.")

    new_request = FriendRequest(sender_id=sender_id, receiver_id=target_user.id)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {"status": 200, "message": "친구 추가 요청이 전송됐습니다."}


# ✅ 3. 친구 요청 수락/거절
@router.put("/accept")
def handle_friend_request(request: FriendAcceptRequest, receiver_id: str = Query(...), db: Session = Depends(get_db)):
    """
    친구 요청을 수락하거나 거절합니다.
    """
    friend_request = (
        db.query(FriendRequest)
        .filter(FriendRequest.receiver_id == receiver_id, FriendRequest.status == FriendStatus.pending)
        .first()
    )

    if not friend_request:
        raise HTTPException(status_code=404, detail="대기 중인 친구 요청이 없습니다.")

    if request.action == "accept":
        friend_request.status = FriendStatus.accepted
        message = "친구 추가가 수락되었습니다."
    elif request.action == "reject":
        friend_request.status = FriendStatus.rejected
        message = "친구 요청이 거절되었습니다."
    else:
        raise HTTPException(status_code=400, detail="action은 'accept' 또는 'reject' 여야 합니다.")

    db.commit()
    return {"status": 200, "message": message}
