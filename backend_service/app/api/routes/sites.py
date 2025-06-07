"""
站点管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.get("/", summary="获取站点列表")
async def get_sites(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取站点列表"""
    # 简化实现，返回示例数据
    return {
        "items": [
            {
                "id": 1,
                "name": "总部大厦",
                "code": "HQ001",
                "address": "北京市朝阳区中关村大街1号",
                "status": "active"
            }
        ],
        "total": 1
    }


@router.get("/{site_id}", summary="获取站点详情")
async def get_site(
    site_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取站点详情"""
    # 简化实现
    if site_id == 1:
        return {
            "id": 1,
            "name": "总部大厦",
            "code": "HQ001",
            "address": "北京市朝阳区中关村大街1号",
            "city": "北京",
            "province": "北京市",
            "status": "active",
            "working_hours_start": "09:00",
            "working_hours_end": "18:00"
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="站点不存在"
    ) 