from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignup(BaseModel):
    id: str
    password: str
    nickname: str
    address: str
    email: EmailStr
    birth: str
    agreedToTerms: bool

class UserLogin(BaseModel):
    id: str
    password: str

class CheckEmail(BaseModel):
    email: EmailStr

class CheckNickname(BaseModel):
    nickname: str

class PasswordReset(BaseModel):
    new_password: str
