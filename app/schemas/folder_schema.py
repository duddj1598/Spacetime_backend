from pydantic import BaseModel
from typing import Optional

# ⭐️ 기존 스키마 유지 ⭐️

class FolderCreate(BaseModel):
    title: str
    user_id: str
    main_folder_img: Optional[str] = None
    is_public: Optional[bool] = False

class FolderResponse(BaseModel):
    folder_id: int
    title: str
    main_folder_img: Optional[str]

    class Config:
        orm_mode = True

# ⭐️ FolderUpdate 스키마 추가 (오류 해결) ⭐️
class FolderUpdate(BaseModel):
    """
    폴더 정보 수정을 위한 스키마입니다.
    수정은 선택 사항이므로 모든 필드는 Optional입니다.
    """
    title: Optional[str] = None
    main_folder_img: Optional[str] = None
    is_public: Optional[bool] = None
    
    # Pydantic V1 설정이 기존 코드에 있으므로, orm_mode도 추가해줍니다.
    class Config:
        orm_mode = True 
        # Pydantic V2를 사용한다면: from_attributes = True

class FolderVisibilityUpdate(BaseModel):
    is_public: bool