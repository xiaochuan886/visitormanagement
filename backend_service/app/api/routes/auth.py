"""
认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.infrastructure.auth.jwt_handler import jwt_handler

router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(login_data: LoginRequest):
    """用户登录"""
    # 这里应该验证用户凭据，简化演示直接返回令牌
    # 实际项目中需要验证用户名密码，查询用户信息
    
    if login_data.username == "admin" and login_data.password == "admin123":
        # 创建令牌
        tokens = jwt_handler.create_user_tokens(
            user_id="1",
            username=login_data.username,
            tenant_id="default",
            roles=["admin"],
            permissions=["visitor:read", "visitor:write", "visitor:delete"]
        )
        
        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=jwt_handler.access_token_expire_minutes * 60
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或密码错误"
    )


@router.post("/refresh", response_model=dict, summary="刷新访问令牌")
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = jwt_handler.verify_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id", "default")
        
        # 创建新的访问令牌
        token_data = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "roles": ["admin"],  # 实际项目中应从数据库获取
            "permissions": ["visitor:read", "visitor:write", "visitor:delete"]
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": jwt_handler.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )


@router.post("/logout", summary="用户登出")
async def logout():
    """用户登出"""
    # 在实际项目中，可能需要将令牌加入黑名单
    return {"message": "登出成功"}


@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user: dict = Depends(jwt_handler.verify_token)):
    """获取当前用户信息"""
    return {
        "user_id": current_user.get("sub"),
        "username": current_user.get("username"),
        "tenant_id": current_user.get("tenant_id"),
        "roles": current_user.get("roles", []),
        "permissions": current_user.get("permissions", [])
    } 