"""
站点管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.tenant import get_current_tenant
from app.application.dto.site_dto import (
    SiteCreateDTO,
    SiteUpdateDTO,
    SiteResponseDTO,
    SiteListResponseDTO,
    SiteQueryDTO
)
from app.application.services.site_service import SiteService
from app.domain.base_enums import SiteStatus

router = APIRouter()


@router.post("/", response_model=SiteResponseDTO, summary="创建站点")
async def create_site(
    site_data: SiteCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """创建新站点"""
    try:
        service = SiteService(db)
        return await service.create_site(site_data, current_user["sub"], tenant_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=SiteListResponseDTO, summary="获取站点列表")
async def get_sites(
    name: str = Query(None, description="站点名称"),
    code: str = Query(None, description="站点编码"),
    city: str = Query(None, description="城市"),
    province: str = Query(None, description="省份"),
    status: SiteStatus = Query(None, description="站点状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取站点列表"""
    query_params = SiteQueryDTO(
        name=name,
        code=code,
        city=city,
        province=province,
        status=status,
        page=page,
        page_size=page_size
    )
    service = SiteService(db)
    return await service.get_sites(query_params, tenant_id)


@router.get("/{site_id}", response_model=SiteResponseDTO, summary="获取站点详情")
async def get_site(
    site_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """获取站点详情"""
    service = SiteService(db)
    site = await service.get_site_by_id(site_id, tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    return site


@router.put("/{site_id}", response_model=SiteResponseDTO, summary="更新站点信息")
async def update_site(
    site_id: int,
    site_data: SiteUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """更新站点信息"""
    try:
        service = SiteService(db)
        site = await service.update_site(
            site_id, site_data, current_user["sub"], tenant_id
        )
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="站点不存在"
            )
        return site
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{site_id}", summary="删除站点")
async def delete_site(
    site_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
):
    """删除站点"""
    service = SiteService(db)
    success = await service.delete_site(site_id, current_user["sub"], tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="站点不存在"
        )
    return {"message": "站点删除成功"} 