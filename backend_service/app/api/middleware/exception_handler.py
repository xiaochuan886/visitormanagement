"""
全局异常处理中间件
"""
import logging
import traceback
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class CustomException(Exception):
    """自定义业务异常基类"""
    
    def __init__(self, message: str, code: str = "BUSINESS_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class VisitorNotFoundException(CustomException):
    """访客未找到异常"""
    
    def __init__(self, visitor_id: str):
        super().__init__(
            message=f"访客ID {visitor_id} 不存在",
            code="VISITOR_NOT_FOUND",
            status_code=404
        )


class UnauthorizedException(CustomException):
    """未授权异常"""
    
    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )


class ForbiddenException(CustomException):
    """权限不足异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403
        )


class ValidationException(CustomException):
    """数据验证异常"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422
        )


async def exception_handler_middleware(request: Request, call_next):
    """全局异常处理中间件"""
    try:
        return await call_next(request)
    except Exception as exc:
        return await handle_exception(request, exc)


async def handle_exception(request: Request, exc: Exception) -> JSONResponse:
    """统一异常处理函数"""
    
    # 获取请求信息用于日志
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None
    }
    
    # HTTP异常
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTP异常: {exc.detail}", extra={"request": request_info})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "type": "HTTPException"
                },
                "data": None
            }
        )
    
    # 自定义业务异常
    if isinstance(exc, CustomException):
        logger.warning(f"业务异常: {exc.message}", extra={"request": request_info})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "type": "BusinessException"
                },
                "data": None
            }
        )
    
    # Pydantic验证异常
    if isinstance(exc, ValidationError):
        logger.warning(f"数据验证异常: {str(exc)}", extra={"request": request_info})
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "type": "ValidationError",
                    "details": errors
                },
                "data": None
            }
        )
    
    # SQLAlchemy数据库异常
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"数据库异常: {str(exc)}", extra={"request": request_info})
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "数据库操作失败",
                    "type": "DatabaseException"
                },
                "data": None
            }
        )
    
    # 未知异常
    logger.error(
        f"未处理的异常: {type(exc).__name__}: {str(exc)}",
        extra={
            "request": request_info,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "type": "InternalServerError"
            },
            "data": None
        }
    ) 