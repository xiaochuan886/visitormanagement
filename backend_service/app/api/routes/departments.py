"""
部门管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.get("/", summary="获取部门列表")
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取部门列表"""
    # 简化实现，返回示例数据
    return {
        "items": [
            {
                "id": 1,
                "name": "技术部",
                "code": "TECH",
                "description": "技术开发部门",
                "parent_id": None
            },
            {
                "id": 2,
                "name": "人力资源部",
                "code": "HR",
                "description": "人力资源管理部门",
                "parent_id": None
            }
        ],
        "total": 2
    }


@router.get("/{department_id}", summary="获取部门详情")
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取部门详情"""
    # 简化实现
    if department_id in [1, 2]:
        departments = {
            1: {
                "id": 1,
                "name": "技术部",
                "code": "TECH",
                "description": "技术开发部门",
                "parent_id": None
            },
            2: {
                "id": 2,
                "name": "人力资源部",
                "code": "HR", 
                "description": "人力资源管理部门",
                "parent_id": None
            }
        }
        return departments[department_id]
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="部门不存在"
    ) 