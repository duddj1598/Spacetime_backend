from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.folder_model import Folder
from app.models.diary_model import Diary
from app.schemas.folder_schema import FolderCreate
from app.schemas.diary_schema import DiaryCreate 


router = APIRouter(prefix="/api/folder", tags=["Folder"])


# ✅ 1. 내 폴더 조회 (그대로 유지)
@router.get("/list/me")
def get_my_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
    folders = db.query(Folder).filter(Folder.user_id == user_id).all()
    data = [{"title": f.title, "folder_id": f.folder_id} for f in folders]
    return {"status": 200, "folders": data}


# ✅ 2. 친구 폴더 조회 (공개 폴더만)
@router.get("/list/friend")
def get_friend_folders(user_id: str = Query(...), db: Session = Depends(get_db)):
    folders = (
        db.query(Folder)
        .filter(Folder.user_id == user_id, Folder.is_public == True)
        .all()
    )
    data = [{"title": f.title, "folder_id": f.folder_id} for f in folders]
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


# ✅ 5. 폴더 생성 (그대로 유지)
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


# ✅ 6. 일기 작성 (DiaryCreate 스키마에 맞게 수정)
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
        theme=data.theme,
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
