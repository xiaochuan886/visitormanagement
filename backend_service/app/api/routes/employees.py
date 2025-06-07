"""
员工管理API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant

router = APIRouter()


@router.get("/", summary="获取员工列表")
async def get_employees(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取员工列表"""
    # 简化实现，返回示例数据
    return {
        "items": [
            {
                "id": 1,
                "name": "张三",
                "email": "zhangsan@company.com",
                "phone_number": "13800138001",
                "department_id": 1,
                "status": "active"
            }
        ],
        "total": 1,
        "page": page,
        "page_size": page_size,
        "total_pages": 1
    }


@router.get("/{employee_id}", summary="获取员工详情")
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取员工详情"""
    # 简化实现
    if employee_id == 1:
        return {
            "id": 1,
            "name": "张三",
            "email": "zhangsan@company.com",
            "phone_number": "13800138001",
            "department_id": 1,
            "status": "active"
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="员工不存在"
    ) 