from pydantic import BaseModel
from typing import Optional, List, Dict

# location은 { "lat": float, "lng": float } 구조로 사용
Location = Dict[str, float]


class DiaryCreate(BaseModel):
    folder_id: int
    title: str
    content: str
    photos: Optional[List[str]] = None
    date: Optional[str] = None  # "YYYY-MM-DD" 형식
    location: Optional[Location] = None   # {"lat": ..., "lng": ...}


class DiaryDetailResponse(BaseModel):
    diary_id: int
    title: str
    content: str
    theme: Optional[str]
    photos: Optional[List[str]] = None
    location: Optional[Location] = None

    class Config:
        orm_mode = True
