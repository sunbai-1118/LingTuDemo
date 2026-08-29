from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, require_admin
from app.core.response import ok
from app.models.user import User

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("/a")
def resource_a(user: User = Depends(get_current_user)):
    """所有登录用户可访问（USER / ADMIN）。"""
    return ok(
        {
            "resource": "A",
            "message": f"你好 {user.username}，这是资源 A，所有登录用户可见。",
        }
    )


@router.get("/b")
def resource_b(user: User = Depends(require_admin)):
    """仅 ADMIN 可访问；USER 会收到 403。"""
    return ok(
        {
            "resource": "B",
            "message": f"你好 {user.username}，这是资源 B，仅管理员可见。",
        }
    )
