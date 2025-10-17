from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# FastAPI 애플리케이션 생성
app = FastAPI()

# -----------------
# 1. CORS 설정 (필수)
# -----------------
# React 클라이언트의 요청을 허용하기 위해 모든 출처(*)를 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# -----------------
# 2. 데이터 모델 정의
# -----------------
# 클라이언트로부터 받을 데이터 구조 (간단하게 name 필드만 정의)
class ClientData(BaseModel):
    name: str

# -----------------
# 3. API 엔드포인트 정의
# -----------------
@app.post("/api/check")
def check_connection(data: ClientData):
    """
    클라이언트로부터 데이터를 받아, 연동 성공 메시지와 함께 반환합니다.
    """
    # 클라이언트가 보낸 이름을 포함하여 응답 메시지 생성
    response_message = f"서버 연동 성공 (Port 8080)! 받은 데이터: {data.name}"
    
    # 이 메시지를 클라이언트로 JSON 형태로 반환
    return {"status": "success", "message": response_message}

# 서버 시작 시 메시지 출력 (8080 포트 명시)
@app.on_event("startup")
async def startup_event():
    print("FastAPI 서버 시작: http://localhost:8080")
    print("클라이언트 연동 준비 완료.")