from pydantic import BaseModel
from typing import Optional

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
