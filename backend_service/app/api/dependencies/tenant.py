"""
多租户依赖注入
"""
from typing import Dict, Any
from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.core.config import settings


async def get_current_tenant(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """获取当前租户ID"""
    tenant_id = current_user.get("tenant_id")
    
    if not tenant_id:
        # 如果令牌中没有租户ID，使用默认租户
        tenant_id = settings.default_tenant_id
    
    return tenant_id


async def get_current_tenant_optional(
    current_user: Dict[str, Any] = None
) -> str:
    """获取当前租户ID（可选）"""
    if current_user and current_user.get("tenant_id"):
        return current_user["tenant_id"]
    
    return settings.default_tenant_id


def require_tenant(allowed_tenants: list[str] = None):
    """租户检查装饰器"""
    def tenant_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
        tenant_id: str = Depends(get_current_tenant)
    ):
        if allowed_tenants and tenant_id not in allowed_tenants:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"租户 {tenant_id} 无权访问此资源"
            )
        
        return {"user": current_user, "tenant_id": tenant_id}
    
    return tenant_checker 