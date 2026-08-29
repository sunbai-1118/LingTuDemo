from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

USERNAME_MIN, USERNAME_MAX = 3, 20
PASSWORD_MIN, PASSWORD_MAX = 8, 64


class RegisterRequest(BaseModel):
    username: str = Field(min_length=USERNAME_MIN, max_length=USERNAME_MAX)
    password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)
    confirm_password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)

    @field_validator("username")
    @classmethod
    def username_charset(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("用户名不能为空")
        if any(ch.isspace() for ch in v):
            raise ValueError("用户名不能包含空白字符")
        return v


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=USERNAME_MAX)
    password: str = Field(min_length=1, max_length=PASSWORD_MAX)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    status: str
    created_at: datetime


class LoginData(BaseModel):
    token: str
    user: UserOut
