from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth_schema import (
    UserSignup,
    UserLogin,
    CheckEmail,
    CheckNickname,
    PasswordReset,
)
from app.models.user_model import User
from app.database import get_db
from app.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ✅ 회원가입 (spacetime.db에 실제 저장)
@router.post("/signup")
def signup(data: UserSignup, db: Session = Depends(get_db)):
    print("Signup data received:", data)
    # 중복 검사 (id, nickname, email)
    if db.query(User).filter(User.id == data.id).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    if db.query(User).filter(User.nickname == data.nickname).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다.")

    # 신규 유저 생성 후 DB 저장
    new_user = User(
        id=data.id,
        password=data.password,
        nickname=data.nickname,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입이 성공적으로 완료되었습니다."}


# ✅ 로그인
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.id).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    token = create_access_token({"sub": user.id})
    return {"status": 200, "accessToken": token}


# ✅ 이메일 중복 확인
@router.post("/check-email")
def check_email(data: CheckEmail, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        return {"message": "이미 사용 중인 이메일입니다."}
    return {"message": "사용 가능한 이메일입니다."}


# ✅ 닉네임 중복 확인
@router.post("/check-nickname")
def check_nickname(data: CheckNickname, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.nickname == data.nickname).first()
    if exists:
        return {"message": "이미 사용 중인 닉네임입니다."}
    return {"message": "사용 가능한 닉네임입니다."}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth_schema import (
    UserSignup,
    UserLogin,
    CheckEmail,
    CheckNickname,
    PasswordReset,
)
from app.models.user_model import User
from app.database import get_db
from app.utils.jwt_handler import create_access_token

import smtplib
from email.mime.text import MIMEText
import random

# 🔥 임시로 인증번호 저장 (실서비스는 Redis 권장)
TEMP_CODES = {}

# -----------------------------
# 1) 이메일로 인증번호 전송
# -----------------------------
@router.post("/send-code")
def send_code(data: CheckEmail, db: Session = Depends(get_db)):

    email = data.email

    # 인증번호 생성
    code = str(random.randint(100000, 999999))
    TEMP_CODES[email] = code

    # SMTP 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "hellojuno6649@gmail.com"
    sender_password = "gwva wjuj hxet twud"  # 앱 비밀번호 사용

    msg = MIMEText(f"비밀번호 재설정 인증번호는 [{code}] 입니다.")
    msg["Subject"] = "Spacetime 비밀번호 재설정 인증번호"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
    except Exception as e:
        print("SMTP Error:", e)
        raise HTTPException(status_code=500, detail="메일 전송에 실패했습니다.")

    return {"status": 200, "message": "인증번호가 이메일로 전송되었습니다."}


# -----------------------------
# 2) 인증번호 검증
# -----------------------------
@router.post("/verify-code")
def verify_code(payload: dict):

    email = payload.get("email")
    code = payload.get("code")

    if email not in TEMP_CODES:
        raise HTTPException(status_code=400, detail="인증 요청 이력이 없습니다.")

    if TEMP_CODES[email] != code:
        raise HTTPException(status_code=400, detail="인증번호가 올바르지 않습니다.")

    return {
        "status": 200,
        "verified": True,
        "message": "인증번호가 일치합니다."
    }

# ✅ 비밀번호 재설정 (예시)
@router.put("/password/reset")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="사용자를 찾을 수 없습니다.")

    user.password = data.new_password
    db.commit()
    return {"status":200,"message": "비밀번호가 성공적으로 변경되었습니다."}
