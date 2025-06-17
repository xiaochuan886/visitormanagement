"""
部门管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant
from app.application.dto.department_dto import (
    DepartmentCreateDTO,
    DepartmentUpdateDTO,
    DepartmentResponseDTO,
    DepartmentListResponseDTO,
    DepartmentQueryDTO
)
from app.application.services.department_service import DepartmentService
from app.domain.base_enums import EmployeeStatus

router = APIRouter()


@router.post("/", response_model=DepartmentResponseDTO, summary="创建部门")
async def create_department(
    department_data: DepartmentCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """创建新部门"""
    try:
        service = DepartmentService(db)
        return await service.create_department(department_data, current_user["sub"], tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=DepartmentListResponseDTO, summary="获取部门列表")
async def get_departments(
    name: str = Query(None, description="部门名称"),
    code: str = Query(None, description="部门编码"),
    parent_id: int = Query(None, description="上级部门ID"),
    manager_id: int = Query(None, description="部门经理ID"),
    site_id: int = Query(None, description="所属站点ID"),
    status: EmployeeStatus = Query(None, description="部门状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取部门列表"""
    query_params = DepartmentQueryDTO(
        name=name,
        code=code,
        parent_id=parent_id,
        manager_id=manager_id,
        site_id=site_id,
        status=status,
        page=page,
        page_size=page_size
    )
    service = DepartmentService(db)
    return await service.get_departments(query_params, tenant_id)


@router.get("/{department_id}", response_model=DepartmentResponseDTO, summary="获取部门详情")
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取部门详情"""
    service = DepartmentService(db)
    department = await service.get_department_by_id(department_id, tenant_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    return department


@router.put("/{department_id}", response_model=DepartmentResponseDTO, summary="更新部门信息")
async def update_department(
    department_id: int,
    department_data: DepartmentUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """更新部门信息"""
    try:
        service = DepartmentService(db)
        department = await service.update_department(
            department_id, department_data, current_user["sub"], tenant_id
        )
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        return department
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{department_id}", summary="删除部门")
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """删除部门"""
    try:
        service = DepartmentService(db)
        success = await service.delete_department(department_id, current_user["sub"], tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        return {"message": "部门删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 