from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------
# 조회 시 사용되는 스키마
# ---------------------------------------------------------
class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# 수정 요청 스키마
# ---------------------------------------------------------
class UserEdit(BaseModel):
    user_id: str
    profile_image: Optional[str] = None
    nickname: Optional[str] = None
    name: Optional[str] = None
