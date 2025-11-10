from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserSignup, UserLogin
from app.models.user_model import User
from app.database import get_db
from app.utils.jwt_handler import create_access_token
from app.schemas.user_schema import (
    UserSignup,
    UserLogin,
    CheckEmail,
    CheckNickname,
    PasswordReset,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# 회원가입
@router.post("/signup")
def signup(data: UserSignup, db: Session = Depends(get_db)):
    # ID 중복 검사
    if db.query(User).filter(User.id == data.id).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    # 닉네임 중복 검사
    if db.query(User).filter(User.nickname == data.nickname).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다.")

    # 이메일 중복 검사
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    # 신규 유저 생성
    new_user = User(**data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입이 성공적으로 완료되었습니다."}


# 로그인
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.id).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    token = create_access_token({"sub": user.id})
    return {"status": 200, "accessToken": token}


# 3. 이메일 중복확인
@router.post("/check-email")
def check_email(data: CheckEmail):
    for user in fake_users_db.values():
        if user["email"] == data.email:
            return {"message": "이미 사용 중인 이메일입니다."}
    return {"message": "사용 가능한 이메일입니다."}

# 4. 닉네임 중복확인
@router.post("/check-nickname")
def check_nickname(data: CheckNickname):
    for user in fake_users_db.values():
        if user["nickname"] == data.nickname:
            return {"message": "이미 사용 중인 닉네임입니다."}
    return {"message": "사용 가능한 닉네임입니다."}

# 5. 비밀번호 변경
@router.put("/password/reset")
def reset_password(data: PasswordReset):
    for user_id, user in fake_users_db.items():
        if data.question_answer == "한성초등학교":  # 실제론 검증 로직 필요
            user["password"] = data.new_password
            return {"message": "비밀번호가 성공적으로 변경되었습니다."}
    raise HTTPException(status_code=400, detail="질문 답변이 올바르지 않습니다.")
