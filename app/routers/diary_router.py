from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.diary_model import Diary
from app.models.folder_model import Folder

router = APIRouter(prefix="/api/diary", tags=["Diary"])


# ✅ 일기 상세 조회 (기존 기능 유지 + photos, location 추가)
@router.get("/detail")
def get_diary_detail(diary_id: int = Query(...), db: Session = Depends(get_db)):
    diary = db.query(Diary).filter(Diary.diary_id == diary_id).first()
    if not diary:
        raise HTTPException(status_code=404, detail="일기를 찾을 수 없습니다.")

    return {
        "status": 200,
        "diary": {
            "diary_id": diary.diary_id,
            "folder_id" : diary.folder_id,
            "title": diary.title,
            "content": diary.content,
            "photos": diary.photos or [],
            "location": diary.location,
        },
    }


# ✅ 폴더 공개 설정 (기존 그대로 유지)
@router.post("/public")
def set_folder_public(
    folder_id: int = Query(...),
    diary_public: bool = Query(...),
    db: Session = Depends(get_db),
):
    folder = db.query(Folder).filter(Folder.folder_id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="폴더를 찾을 수 없습니다.")
    folder.is_public = diary_public
    db.commit()
    return {"message": "공개가 완료되었습니다." if diary_public else "비공개로 변경되었습니다."}
