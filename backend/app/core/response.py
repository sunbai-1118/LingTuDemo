"""Unified API response helpers.

Response shape: {"code": int, "message": str, "data": ...}
HTTP status codes are kept meaningful; `code` mirrors them for convenience.
"""
from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "success", status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": data},
    )


def fail(message: str, status_code: int, data: Any = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": data},
    )
