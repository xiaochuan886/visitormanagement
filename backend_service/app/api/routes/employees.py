"""
员工管理API路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant
from app.application.dto.employee_dto import (
    EmployeeCreateDTO,
    EmployeeUpdateDTO,
    EmployeeResponseDTO,
    EmployeeListResponseDTO,
    EmployeeQueryDTO
)
from app.application.services.employee_service import EmployeeService
from app.domain.base_enums import EmployeeStatus

router = APIRouter()


@router.post("/", response_model=EmployeeResponseDTO, summary="创建员工")
async def create_employee(
    employee_data: EmployeeCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """创建新员工"""
    try:
        service = EmployeeService(db)
        return await service.create_employee(employee_data, current_user["sub"], tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=EmployeeListResponseDTO, summary="获取员工列表")
async def get_employees(
    name: str = Query(None, description="员工姓名"),
    employee_id: str = Query(None, description="员工工号"),
    email: str = Query(None, description="邮箱地址"),
    department_id: int = Query(None, description="部门ID"),
    position: str = Query(None, description="职位"),
    manager_id: int = Query(None, description="直属上级ID"),
    status: EmployeeStatus = Query(None, description="员工状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取员工列表"""
    query_params = EmployeeQueryDTO(
        name=name,
        employee_id=employee_id,
        email=email,
        department_id=department_id,
        position=position,
        manager_id=manager_id,
        status=status,
        page=page,
        page_size=page_size
    )
    service = EmployeeService(db)
    return await service.get_employees(query_params, tenant_id)


@router.get("/{employee_id}", response_model=EmployeeResponseDTO, summary="获取员工详情")
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取员工详情"""
    service = EmployeeService(db)
    employee = await service.get_employee_by_id(employee_id, tenant_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponseDTO, summary="更新员工信息")
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """更新员工信息"""
    try:
        service = EmployeeService(db)
        employee = await service.update_employee(
            employee_id, employee_data, current_user["sub"], tenant_id
        )
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="员工不存在"
            )
        return employee
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{employee_id}", summary="删除员工")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """删除员工"""
    try:
        service = EmployeeService(db)
        success = await service.delete_employee(employee_id, current_user["sub"], tenant_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="员工不存在"
            )
        return {"message": "员工删除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 