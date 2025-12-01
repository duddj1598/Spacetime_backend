from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.folder_model import Folder
from app.models.diary_model import Diary
from app.models.friend_model import FriendRequest, FriendStatus
from app.models.user_model import User
from app.schemas.folder_schema import FolderCreate, FolderUpdate, FolderVisibilityUpdate
from app.schemas.diary_schema import DiaryCreate 
from typing import Optional 

router = APIRouter(prefix="/api/folder", tags=["Folder"])


# ✅ 1. 내 폴더 조회
@router.get("/list/me")
def get_my_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
    folders = db.query(Folder).filter(Folder.user_id == user_id).all()
    
    data = []
    for f in folders:
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


# ✅ 2. 친구 폴더 조회 (공개된 것만)
@router.get("/list/friends")
def get_friends_public_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
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
    
    friend_ids = []
    for f in sent_friends:
        friend_ids.append(f.receiver_id)
    for f in received_friends:
        friend_ids.append(f.sender_id)
    
    if not friend_ids:
        return {"status": 200, "folders": []}
    
    folders = (
        db.query(Folder)
        .filter(
            Folder.user_id.in_(friend_ids),
            Folder.is_public == True
        )
        .all()
    )
    
    data = []
    for f in folders:
        owner = db.query(User).filter(User.id == f.user_id).first()
        
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


# ✅ 3. 해시태그 폴더 조회
@router.get("/list/global")
def get_global_folders(hashtag: str = Query(...), db: Session = Depends(get_db)):
    folders = (
        db.query(Folder)
        .filter(Folder.is_public == True, Folder.title.contains(hashtag))
        .all()
    )
    data = [{"title": f.title, "folder_id": f.folder_id} for f in folders]
    return {"status": 200, "folders": data}


# ✅ 4. 폴더 상세 조회
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


# ✅ 5. 친구 폴더 상세 조회 (공개 여부 확인)
@router.get("/detail/shared")
def get_shared_folder_detail(
    folder_id: int = Query(...),
    current_user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")

    if folder.user_id == current_user_id or folder.is_public:
        return get_folder_detail(folder_id=folder_id, db=db)
    else:
        raise HTTPException(status_code=403, detail="이 폴더를 조회할 권한이 없습니다.")


# ✅ 6. 폴더 생성
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


# ⭐️ 6-1. 폴더 공개 설정 변경 (새로 추가!)
@router.put("/{folder_id}/visibility")
def update_folder_visibility(
    folder_id: int,
    data: FolderVisibilityUpdate,
    db: Session = Depends(get_db)
):
    """
    폴더의 공개/비공개 설정을 변경합니다.
    """
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")
    
    # 공개 설정 업데이트
    folder.is_public = data.is_public
    db.commit()
    db.refresh(folder)
    
    return {
        "status": 200,
        "message": f"폴더가 {'공개' if data.is_public else '비공개'}로 변경되었습니다.",
        "folder": {
            "folder_id": folder.folder_id,
            "title": folder.title,
            "is_public": folder.is_public
        }
    }


# ✅ 7. 폴더 이름 수정
@router.put("/{folder_id}")
def update_folder_name(
    folder_id: int,
    data: Optional[FolderUpdate] = None, 
    db: Session = Depends(get_db)
):
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")
        
    if data and data.title:
        folder.title = data.title
        db.commit()
        db.refresh(folder)
        return {"status": 200, "message": f"폴더 제목이 '{folder.title}'로 수정되었습니다."}
        
    return {"status": 200, "message": "수정할 내용이 없습니다."}


# ✅ 8. 일기 작성
@router.post("/create")
def create_diary(data: DiaryCreate, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.folder_id == data.folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")

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