import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.auth import router as auth_router
from app.api.resources import router as resources_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.response import fail
from app.core.security import hash_password
from app.repositories.user_repo import UserRepository

logging.basicConfig(level=logging.INFO)


def seed_admin() -> None:
    """保证存在一个可用于测试 Resource B 的管理员账号。"""
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        if repo.get_by_username(settings.admin_username) is None:
            repo.create(
                settings.admin_username,
                hash_password(settings.admin_password),
                role="ADMIN",
            )
            logging.info("Seeded admin account %r", settings.admin_username)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        seed_admin()
    except Exception:
        # 数据库暂时不可用时不要让整个服务无法启动（例如测试环境未配置 MySQL）
        logging.exception("Database init skipped due to error")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resources_router)


@app.get("/api/health")
def health():
    return {"code": 200, "message": "success", "data": {"status": "ok"}}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    msg = str(first.get("msg", "请求参数不合法"))
    # 翻译 pydantic 的英文默认消息为用户可读提示
    if "at least" in msg:
        message = "输入长度不符合要求"
    elif "at most" in msg:
        message = "输入长度不符合要求"
    elif "unable to interpret" in msg or "expected" in msg:
        message = "请求参数类型错误"
    else:
        message = "请求参数不合法"
    return fail(message, 422)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return fail("未登录或登录已过期，请重新登录", 401)
    if exc.status_code == 403:
        detail = exc.detail if isinstance(exc.detail, str) else "没有访问该资源的权限"
        return fail(detail, 403)
    return fail(str(exc.detail) if exc.detail else "请求失败", exc.status_code)


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logging.exception("Unexpected error on %s %s", request.method, request.url.path)
    return fail("服务器内部错误，请稍后重试", 500)
