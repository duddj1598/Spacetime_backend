from pydantic import BaseModel
from typing import Optional, List, Any

class DiaryCreate(BaseModel):
    folder_id: int
    title: str
    content: str
    photos: Optional[List[str]] = None
    theme: Optional[str] = None
    location: Optional[Any] = None

class DiaryDetailResponse(BaseModel):
    diary_id: int
    title: str
    content: str
    theme: Optional[str]
    photos: Optional[List[str]] = None
    location: Optional[Any] = None

    class Config:
        orm_mode = True
