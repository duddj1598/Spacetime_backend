from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.models.notification_model import Notification
from app.schemas.friend_schema import FriendRequestCreate, FriendAcceptRequest

router = APIRouter(prefix="/api/friend", tags=["Friend"])


# ✅ 1️⃣ 친구 목록 조회
@router.get("/list")
def get_friend_list(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    user_id를 기반으로 친구 목록을 조회합니다.
    """
    # 보낸 요청 중 수락된 친구
    sent_friends = (
        db.query(FriendRequest)
        .filter(FriendRequest.sender_id == user_id, FriendRequest.status == FriendStatus.accepted)
        .all()
    )
    # 받은 요청 중 수락된 친구
    received_friends = (
        db.query(FriendRequest)
        .filter(FriendRequest.receiver_id == user_id, FriendRequest.status == FriendStatus.accepted)
        .all()
    )

    friend_list = []

    # 내가 보낸 친구 요청
    for f in sent_friends:
        friend_user = db.query(User).filter(User.id == f.receiver_id).first()
        if friend_user:
            friend_list.append({"nickname": friend_user.nickname, "friend_id": friend_user.id})

    # 내가 받은 친구 요청
    for f in received_friends:
        friend_user = db.query(User).filter(User.id == f.sender_id).first()
        if friend_user:
            friend_list.append({"nickname": friend_user.nickname, "friend_id": friend_user.id})

    return {"status": 200, "friends": friend_list}


# ✅ 2️⃣ 친구 추가 요청
@router.post("/request")
def send_friend_request(request: FriendRequestCreate, sender_id: str = Query(...), db: Session = Depends(get_db)):
    """
    닉네임으로 친구 요청을 전송합니다.
    """
    # 닉네임으로 상대방 유저 찾기
    target_user = db.query(User).filter(User.nickname == request.target_nickname).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="해당 닉네임의 사용자를 찾을 수 없습니다.")

    # 이미 존재하는 요청이나 친구인지 확인
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

    # 새 친구 요청 생성
    new_request = FriendRequest(sender_id=sender_id, receiver_id=target_user.id)
    db.add(new_request)

    # ✅ 알림 추가 (요청 받은 유저에게)
    notification = Notification(user_id=target_user.id, content=f"{sender_id}님이 친구 요청을 보냈습니다.")
    db.add(notification)

    db.commit()
    db.refresh(new_request)

    return {"status": 200, "message": "친구 추가 요청이 전송됐습니다."}


# ✅ 3️⃣ 친구 요청 수락 / 거절
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

    # 수락 / 거절 처리
    if request.action == "accept":
        friend_request.status = FriendStatus.accepted
        message = "친구 추가가 수락되었습니다."
        noti_content = f"{receiver_id}님이 친구 요청을 수락했습니다."
    elif request.action == "reject":
        friend_request.status = FriendStatus.rejected
        message = "친구 요청이 거절되었습니다."
        noti_content = f"{receiver_id}님이 친구 요청을 거절했습니다."
    else:
        raise HTTPException(status_code=400, detail="action은 'accept' 또는 'reject' 여야 합니다.")

    # ✅ 알림 추가 (요청 보낸 유저에게)
    sender_id = friend_request.sender_id
    notification = Notification(user_id=sender_id, content=noti_content)
    db.add(notification)

    db.commit()
    return {"status": 200, "message": message}

@router.get("/pending")
def get_pending_requests(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    user_id 기준으로 대기중인 친구 요청 목록을 반환
    """
    pending_requests = (
        db.query(FriendRequest)
        .filter(
            ((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id)),
            FriendRequest.status == FriendStatus.pending
        )
        .all()
    )

    result = []
    for req in pending_requests:
        other_id = req.receiver_id if req.sender_id == user_id else req.sender_id
        other_user = db.query(User).filter(User.id == other_id).first()

        result.append({
            "friend_id": other_user.id,
            "nickname": other_user.nickname,
            "type": "sent" if req.sender_id == user_id else "received"
        })

    return {"status": 200, "pending": result}

