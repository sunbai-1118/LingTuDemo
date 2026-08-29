import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import fail, ok
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginData, LoginRequest, RegisterRequest, UserOut
from app.services.moderation import ModerationError, moderate_username

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if body.password != body.confirm_password:
        return fail("两次输入的密码不一致", 400)

    repo = UserRepository(db)
    if repo.get_by_username(body.username) is not None:
        return fail("用户名已被占用", 409)

    # LLM 审核失败时 fail closed：拒绝注册，提示稍后重试
    try:
        result = moderate_username(body.username)
    except ModerationError as e:
        return fail(str(e), 503)

    if not result.allowed:
        return fail(f"用户名未通过审核：{result.reason or '包含违规内容'}", 400, {"category": result.category})

    user = repo.create(body.username, hash_password(body.password))
    return ok(UserOut.model_validate(user).model_dump(mode="json"), "注册成功")


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_username(body.username)
    # 统一提示，不区分“用户不存在”和“密码错误”，避免用户名枚举
    if user is None or not verify_password(body.password, user.password_hash):
        return fail("用户名或密码错误", 401)
    if user.status != "ACTIVE":
        return fail("账号已被禁用", 403)

    token = create_access_token(user.id, user.role)
    data = LoginData(token=token, user=UserOut.model_validate(user))
    return ok(data.model_dump(mode="json"), "登录成功")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(current_user).model_dump(mode="json"))
