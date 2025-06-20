"""
访客管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.dto.visitor_dto import (
    VisitorCreateDTO,
    VisitorUpdateDTO,
    VisitorResponseDTO,
    VisitorListResponseDTO,
    VisitorApprovalDTO,
    VisitorCheckinDTO,
    VisitorCheckoutDTO,
    VisitorQueryDTO
)
from app.application.services.visitor_service import VisitorService
from app.api.dependencies.auth import get_current_user, get_current_user_optional
from app.api.dependencies.tenant import get_current_tenant, get_current_tenant_optional

router = APIRouter()


@router.post("/apply", response_model=VisitorResponseDTO, summary="访客自主申请（无需登录）")
async def apply_visitor(
    visitor_data: VisitorCreateDTO,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_optional)
):
    """访客自主申请，无需登录认证"""
    service = VisitorService(db)
    # 匿名创建，传入None作为创建者ID
    return await service.create_visitor(visitor_data, None, tenant_id or "default")


@router.get("/query/by-phone", response_model=List[VisitorResponseDTO], summary="通过手机号查询访客申请状态")
async def query_visitor_by_phone(
    phone_number: str = Query(..., description="手机号码"),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_optional)
):
    """通过手机号查询访客申请状态，无需登录"""
    service = VisitorService(db)
    visitors = await service.get_visitors_by_phone(phone_number, tenant_id or "default")
    return visitors


@router.post("/", response_model=VisitorResponseDTO, summary="创建访客（管理员）")
async def create_visitor(
    visitor_data: VisitorCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """管理员创建访客"""
    service = VisitorService(db)
    return await service.create_visitor(visitor_data, current_user["sub"], tenant_id)


@router.get("/", response_model=VisitorListResponseDTO, summary="获取访客列表")
async def get_visitors(
    name: str = Query(None, description="访客姓名"),
    phone_number: str = Query(None, description="电话号码"),
    email: str = Query(None, description="邮箱"),
    status: str = Query(None, description="访客状态"),
    employee_id: int = Query(None, description="被访问员工ID"),
    site_id: int = Query(None, description="站点ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取访客列表"""
    query_params = VisitorQueryDTO(
        name=name,
        phone_number=phone_number,
        email=email,
        status=status,
        employee_id=employee_id,
        site_id=site_id,
        page=page,
        page_size=page_size
    )
    service = VisitorService(db)
    return await service.get_visitors(query_params, tenant_id)


@router.get("/{visitor_id}", response_model=VisitorResponseDTO, summary="获取访客详情")
async def get_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取访客详情"""
    service = VisitorService(db)
    visitor = await service.get_visitor_by_id(visitor_id, tenant_id)
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return visitor


@router.put("/{visitor_id}", response_model=VisitorResponseDTO, summary="更新访客信息")
async def update_visitor(
    visitor_id: int,
    visitor_data: VisitorUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """更新访客信息"""
    service = VisitorService(db)
    visitor = await service.update_visitor(
        visitor_id, visitor_data, current_user["sub"], tenant_id
    )
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return visitor


@router.delete("/{visitor_id}", summary="删除访客")
async def delete_visitor(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """删除访客"""
    service = VisitorService(db)
    success = await service.delete_visitor(visitor_id, current_user["sub"], tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return {"message": "访客删除成功"}


@router.post("/{visitor_id}/approve", response_model=VisitorResponseDTO, summary="审批访客")
async def approve_visitor(
    visitor_id: int,
    approval_data: VisitorApprovalDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """审批访客"""
    service = VisitorService(db)
    visitor = await service.approve_visitor(
        visitor_id, approval_data, current_user["sub"], tenant_id
    )
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return visitor


@router.post("/{visitor_id}/checkin", response_model=VisitorResponseDTO, summary="访客签到")
async def checkin_visitor(
    visitor_id: int,
    checkin_data: VisitorCheckinDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """访客签到"""
    service = VisitorService(db)
    visitor = await service.checkin_visitor(
        visitor_id, checkin_data, current_user["sub"], tenant_id
    )
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在或无法签到"
        )
    return visitor


@router.post("/{visitor_id}/checkout", response_model=VisitorResponseDTO, summary="访客签出")
async def checkout_visitor(
    visitor_id: int,
    checkout_data: VisitorCheckoutDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """访客签出"""
    service = VisitorService(db)
    visitor = await service.checkout_visitor(
        visitor_id, checkout_data, current_user["sub"], tenant_id
    )
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在或无法签出"
        )
    return visitor


@router.get("/{visitor_id}/qrcode", summary="获取访客二维码")
async def get_visitor_qrcode(
    visitor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取访客二维码"""
    service = VisitorService(db)
    qr_code_url = await service.generate_visitor_qrcode(visitor_id, tenant_id)
    if not qr_code_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return {"qr_code_url": qr_code_url} 