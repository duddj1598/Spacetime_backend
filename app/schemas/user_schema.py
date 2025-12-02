from pydantic import BaseModel
from typing import Optional

# ---------------------------------------------------------
# 조회 시 사용되는 스키마
# ---------------------------------------------------------
class UserResponse(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    friend_count: Optional[int] = 0
    monthly_note: Optional[str] = None

    class Config:
        orm_mode = True


# ---------------------------------------------------------
# 수정 요청 스키마 (user_id 제거 - JWT로 처리)
# ---------------------------------------------------------
class UserEdit(BaseModel):
    profile_image: Optional[str] = None
    nickname: Optional[str] = None


# ---------------------------------------------------------
# 이번 달의 한 줄 기록 업데이트 스키마
# ---------------------------------------------------------
class MonthlyNoteUpdate(BaseModel):
    monthly_note: str