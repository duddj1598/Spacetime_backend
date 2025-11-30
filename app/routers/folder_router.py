from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.folder_model import Folder
from app.models.diary_model import Diary
from app.models.friend_model import FriendRequest, FriendStatus
from app.models.user_model import User
from app.schemas.folder_schema import FolderCreate, FolderUpdate 
from app.schemas.diary_schema import DiaryCreate 
from typing import Optional 

router = APIRouter(prefix="/api/folder", tags=["Folder"])


# ✅ 1. 내 폴더 조회 (그대로 유지)
@router.get("/list/me")
def get_my_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
    folders = db.query(Folder).filter(Folder.user_id == user_id).all()
    
    # ⭐️ 응답 형식 개선 - 더 많은 정보 제공 ⭐️
    data = []
    for f in folders:
        # 폴더의 첫 번째 일기 사진 가져오기
        first_diary = db.query(Diary).filter(Diary.folder_id == f.folder_id).first()
        main_img = None
        if first_diary and first_diary.photos:
            main_img = first_diary.photos[0]
        
        data.append({
            "folder_id": f.folder_id,
            "title": f.title,
            "main_folder_img": f.main_folder_img or main_img,
            "is_public": f.is_public,
            "diary_count": db.query(Diary).filter(Diary.folder_id == f.folder_id).count()
        })
    
    return {"status": 200, "folders": data}


# ✅ 2. 친구 폴더 조회 (수정됨) - 친구들의 공개 폴더만
@router.get("/list/friends")
def get_friends_public_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    현재 유저와 친구 관계인 사람들의 공개 폴더를 모두 가져옵니다.
    """
    # 1. 친구 목록 가져오기 (accepted 상태만)
    sent_friends = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.sender_id == user_id,
            FriendRequest.status == FriendStatus.accepted
        )
        .all()
    )
    
    received_friends = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.receiver_id == user_id,
            FriendRequest.status == FriendStatus.accepted
        )
        .all()
    )
    
    # 2. 친구들의 user_id 수집
    friend_ids = []
    for f in sent_friends:
        friend_ids.append(f.receiver_id)
    for f in received_friends:
        friend_ids.append(f.sender_id)
    
    # 3. 친구들의 공개 폴더만 조회
    if not friend_ids:
        return {"status": 200, "folders": []}
    
    folders = (
        db.query(Folder)
        .filter(
            Folder.user_id.in_(friend_ids),  # ✅ 친구들의 폴더
            Folder.is_public == True          # ✅ 공개된 폴더만
        )
        .all()
    )
    
    # 4. 응답 데이터 구성
    data = []
    for f in folders:
        # 폴더 주인 정보
        owner = db.query(User).filter(User.id == f.user_id).first()
        
        # 폴더의 첫 번째 일기 사진 가져오기
        first_diary = db.query(Diary).filter(Diary.folder_id == f.folder_id).first()
        main_img = None
        if first_diary and first_diary.photos:
            main_img = first_diary.photos[0]
        
        data.append({
            "folder_id": f.folder_id,
            "title": f.title,
            "owner_nickname": owner.nickname if owner else "Unknown",
            "owner_id": f.user_id,
            "main_folder_img": f.main_folder_img or main_img,
            "diary_count": db.query(Diary).filter(Diary.folder_id == f.folder_id).count()
        })
    
    return {"status": 200, "folders": data}


# ✅ 3. 해시태그 폴더 조회 (제목 검색)
@router.get("/list/global")
def get_global_folders(hashtag: str = Query(...), db: Session = Depends(get_db)):
    folders = (
        db.query(Folder)
        .filter(Folder.is_public == True, Folder.title.contains(hashtag))
        .all()
    )
    data = [{"title": f.title, "folder_id": f.folder_id} for f in folders]
    return {"status": 200, "folders": data}


# ✅ 4. 폴더 상세 조회 + 지도용 데이터
@router.get("/detail")
def get_folder_detail(folder_id: int = Query(...), db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")

    diaries = db.query(Diary).filter(Diary.folder_id == folder_id).all()

    diary_data = []
    for d in diaries:
        main_photo = d.photos[0] if d.photos else None
        diary_data.append(
            {
                "diary_id": d.diary_id,
                "title": d.title,
                # location: { "lat": ..., "lng": ... } or None
                "location": d.location,
                "main_photo": main_photo,
            }
        )

    return {
        "status": 200,
        "folder": {
            "folder_id": folder.folder_id,
            "title": folder.title,
            "main_folder_img": folder.main_folder_img,
            "is_public": folder.is_public,
            "diaries": diary_data,
        },
    }


# ⭐️ 4-1. 친구 폴더 상세 조회 (추가 기능) ⭐️
@router.get("/detail/shared")
def get_shared_folder_detail(
    folder_id: int = Query(...),
    current_user_id: str = Query(...), # 접근하려는 사용자 ID (로그인 유저)
    db: Session = Depends(get_db)
):
    """
    폴더가 공개 상태인지 확인 후 상세 내용을 반환합니다.
    (내 폴더이거나, 공개 상태일 경우만 허용)
    """
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")

    # 1. 내 폴더이거나 2. 폴더가 공개 설정이어야 접근 허용
    if folder.user_id == current_user_id or folder.is_public:
        # 기존 상세 조회 로직 재사용
        return get_folder_detail(folder_id=folder_id, db=db)
    else:
        raise HTTPException(status_code=403, detail="이 폴더를 조회할 권한이 없습니다.")


# ✅ 5. 폴더 생성
@router.post("")
def create_folder(data: FolderCreate, db: Session = Depends(get_db)):
    new_folder = Folder(
        title=data.title,
        user_id=data.user_id,
        main_folder_img=data.main_folder_img,
        is_public=data.is_public,
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return {
        "status": 200,
        "folder_id": new_folder.folder_id,
        "main_folder_img": new_folder.main_folder_img,
        "message": "정상적으로 폴더가 생성되었습니다.",
    }


# ⭐️ 5-1. 폴더 이름 수정 (추가 기능) ⭐️
@router.put("/{folder_id}")
def update_folder_name(
    folder_id: int,
    data: Optional[FolderUpdate] = None, 
    db: Session = Depends(get_db)
):
    """
    기존 폴더의 제목을 수정합니다.
    """
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")
        
    if data and data.title:
        folder.title = data.title
        db.commit()
        db.refresh(folder)
        return {"status": 200, "message": f"폴더 제목이 '{folder.title}'로 수정되었습니다."}
        
    return {"status": 200, "message": "수정할 내용이 없습니다."}


# ✅ 6. 일기 작성 (AttributeError 수정 완료)
@router.post("/create")
def create_diary(data: DiaryCreate, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.folder_id == data.folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")

    # ⭐️ 오류 수정: data.diary.title 대신 data 객체에서 직접 필드 접근 ⭐️
    new_diary = Diary(
        folder_id=data.folder_id,
        title=data.title,
        content=data.content,
        photos=data.photos,
        location=data.location,
    )
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    return {
        "status": 200,
        "diary_id": new_diary.diary_id,
        "message": "정상적으로 일기를 작성하였습니다.",
    }