"""
认证依赖注入
"""
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.infrastructure.auth.jwt_handler import jwt_handler

# HTTP Bearer认证
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """获取当前用户信息"""
    try:
        # 验证访问令牌
        payload = jwt_handler.verify_token(credentials.credentials)
        
        # 检查令牌类型
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌类型",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查必要字段
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌缺少用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)
) -> Optional[Dict[str, Any]]:
    """获取当前用户信息（完全可选，无token时返回None）"""
    if not credentials:
        return None
    
    try:
        # 验证访问令牌
        payload = jwt_handler.verify_token(credentials.credentials)
        
        # 检查令牌类型
        if payload.get("type") != "access":
            return None
        
        # 检查必要字段
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return payload
        
    except Exception:
        return None


async def get_mobile_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """获取移动端用户信息"""
    try:
        # 验证访问令牌
        payload = jwt_handler.verify_token(credentials.credentials)
        
        # 检查令牌类型（移动端可以是access或mobile类型）
        token_type = payload.get("type")
        if token_type not in ["access", "mobile"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的移动端令牌类型",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查必要字段
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌缺少用户信息",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证移动端权限
        user_roles = payload.get("roles", [])
        mobile_roles = ["gate_operator", "reception_staff", "security_guard", "admin"]
        
        if not any(role in mobile_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户无移动端访问权限"
            )
        
        return payload
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="移动端令牌验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_permissions(required_permissions: list[str]):
    """权限检查装饰器"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        
        # 检查是否有所需权限
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {permission}"
                )
        
        return current_user
    
    return permission_checker


def require_roles(required_roles: list[str]):
    """角色检查装饰器"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        
        # 检查是否有所需角色
        for role in required_roles:
            if role not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少角色: {role}"
                )
        
        return current_user
    
    return role_checker 