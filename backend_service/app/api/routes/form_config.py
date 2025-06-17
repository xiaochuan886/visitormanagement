"""
表单配置管理API
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.services.form_configuration_service import FormConfigurationService
from app.application.dto.form_config_dto import (
    FormConfigurationCreateDTO,
    FormConfigurationUpdateDTO,
    FormConfigurationResponseDTO,
    FormRenderDataDTO,
    FormValidationResultDTO
)
from app.api.dependencies.auth import get_current_user, require_permissions
from app.domain.entities.user import User
from app.core.exceptions import NotFoundError

router = APIRouter()

@router.post(
    "/",
    response_model=FormConfigurationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建表单配置",
    description="创建新的表单配置，支持动态字段定义和验证规则"
)
async def create_form_configuration(
    form_config: FormConfigurationCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建表单配置"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.create_form_configuration(
            tenant_id=current_user.tenant_id,
            form_config=form_config,
            created_by=current_user.username
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建表单配置失败: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[FormConfigurationResponseDTO],
    summary="获取表单配置列表",
    description="获取当前租户的所有表单配置列表，支持分页和筛选"
)
async def list_form_configurations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    form_type: Optional[str] = Query(None, description="表单类型筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取表单配置列表"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.list_form_configurations(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            form_type=form_type,
            is_active=is_active
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表单配置列表失败: {str(e)}"
        )

@router.get(
    "/{config_id}",
    response_model=FormConfigurationResponseDTO,
    summary="获取表单配置详情",
    description="根据配置ID获取表单配置的详细信息"
)
async def get_form_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取表单配置详情"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.get_form_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表单配置失败: {str(e)}"
        )

@router.put(
    "/{config_id}",
    response_model=FormConfigurationResponseDTO,
    summary="更新表单配置",
    description="更新指定的表单配置，支持部分字段更新"
)
async def update_form_configuration(
    config_id: UUID,
    form_config: FormConfigurationUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新表单配置"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.update_form_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            form_config=form_config,
            updated_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新表单配置失败: {str(e)}"
        )

@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除表单配置",
    description="软删除指定的表单配置（实际为停用）"
)
async def delete_form_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除表单配置"""
    service = FormConfigurationService(db)
    
    try:
        success = await service.delete_form_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除表单配置失败: {str(e)}"
        )

@router.get(
    "/{config_id}/render",
    response_model=FormRenderDataDTO,
    summary="获取表单渲染数据",
    description="获取指定表单配置的前端渲染数据，包括字段定义和UI配置"
)
async def get_form_render_data(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取表单渲染数据"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.get_form_render_data(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表单渲染数据失败: {str(e)}"
        )

@router.post(
    "/{config_id}/validate",
    response_model=FormValidationResultDTO,
    summary="验证表单数据",
    description="根据表单配置验证提交的表单数据"
)
async def validate_form_data(
    config_id: UUID,
    form_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """验证表单数据"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.validate_form_data(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            form_data=form_data
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="表单配置不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"表单数据验证失败: {str(e)}"
        )

@router.post(
    "/{config_id}/activate",
    response_model=FormConfigurationResponseDTO,
    summary="激活表单配置",
    description="激活指定的表单配置，使其可用于表单渲染"
)
async def activate_form_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活表单配置"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.activate_form_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"激活表单配置失败: {str(e)}"
        )

@router.post(
    "/{config_id}/deactivate",
    response_model=FormConfigurationResponseDTO,
    summary="停用表单配置",
    description="停用指定的表单配置，使其不可用于表单渲染"
)
async def deactivate_form_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """停用表单配置"""
    service = FormConfigurationService(db)
    
    try:
        result = await service.deactivate_form_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="表单配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"停用表单配置失败: {str(e)}"
        ) 