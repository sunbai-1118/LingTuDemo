"""Authentication & authorization dependencies.

Identity is ALWAYS derived from the JWT in the Authorization header;
user_id / role sent in the request body or query are never trusted.
"""
import jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

_CREDENTIALS_ERROR = HTTPException(
    status_code=401,
    detail="未登录或登录已过期，请重新登录",
)


def _extract_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise _CREDENTIALS_ERROR
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        raise _CREDENTIALS_ERROR
    return token


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = _extract_token(request)
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise _CREDENTIALS_ERROR
    if payload is None:
        raise _CREDENTIALS_ERROR

    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise _CREDENTIALS_ERROR

    user = db.get(User, user_id)
    if user is None or user.status != "ACTIVE":
        raise _CREDENTIALS_ERROR
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="没有访问资源 B 的权限")
    return user
