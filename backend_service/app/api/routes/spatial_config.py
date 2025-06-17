"""
空间配置管理API
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.connection import get_db
from app.application.services.spatial_configuration_service import SpatialConfigurationService
from app.application.dto.spatial_config_dto import (
    SpatialConfigurationCreateDTO,
    SpatialConfigurationUpdateDTO,
    SpatialConfigurationResponseDTO,
    SpatialEntityDTO,
    SpatialHierarchyDTO
)
from app.api.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.core.exceptions import NotFoundError

router = APIRouter()

@router.post(
    "/",
    response_model=SpatialConfigurationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建空间配置",
    description="创建新的空间配置，定义空间层级结构和管理规则"
)
async def create_spatial_configuration(
    spatial_config: SpatialConfigurationCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建空间配置"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.create_spatial_configuration(
            tenant_id=current_user.tenant_id,
            spatial_config=spatial_config,
            created_by=current_user.username
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建空间配置失败: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[SpatialConfigurationResponseDTO],
    summary="获取空间配置列表",
    description="获取当前租户的所有空间配置列表，支持分页和筛选"
)
async def list_spatial_configurations(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间配置列表"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.list_spatial_configurations(
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间配置列表失败: {str(e)}"
        )

@router.get(
    "/{config_id}",
    response_model=SpatialConfigurationResponseDTO,
    summary="获取空间配置详情",
    description="根据配置ID获取空间配置的详细信息"
)
async def get_spatial_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间配置详情"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.get_spatial_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间配置失败: {str(e)}"
        )

@router.put(
    "/{config_id}",
    response_model=SpatialConfigurationResponseDTO,
    summary="更新空间配置",
    description="更新指定的空间配置，支持部分字段更新"
)
async def update_spatial_configuration(
    config_id: UUID,
    spatial_config: SpatialConfigurationUpdateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新空间配置"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.update_spatial_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            spatial_config=spatial_config,
            updated_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新空间配置失败: {str(e)}"
        )

@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除空间配置",
    description="软删除指定的空间配置（实际为停用）"
)
async def delete_spatial_configuration(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除空间配置"""
    service = SpatialConfigurationService(db)
    
    try:
        success = await service.delete_spatial_configuration(
            tenant_id=current_user.tenant_id,
            config_id=config_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间配置不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除空间配置失败: {str(e)}"
        )

@router.get(
    "/{config_id}/hierarchy",
    response_model=SpatialHierarchyDTO,
    summary="获取空间层级结构",
    description="获取指定空间配置的完整层级结构树"
)
async def get_spatial_hierarchy(
    config_id: UUID,
    include_inactive: bool = Query(False, description="是否包含非激活的空间实体"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间层级结构"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.get_spatial_hierarchy(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            include_inactive=include_inactive
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间配置不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间层级结构失败: {str(e)}"
        )

@router.post(
    "/{config_id}/entities",
    response_model=SpatialEntityDTO,
    status_code=status.HTTP_201_CREATED,
    summary="创建空间实体",
    description="在指定的空间配置下创建新的空间实体"
)
async def create_spatial_entity(
    config_id: UUID,
    spatial_entity: SpatialEntityDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建空间实体"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.create_spatial_entity(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            spatial_entity=spatial_entity,
            created_by=current_user.username
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="空间配置不存在"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建空间实体失败: {str(e)}"
        )

@router.get(
    "/{config_id}/entities",
    response_model=List[SpatialEntityDTO],
    summary="获取空间实体列表",
    description="获取指定空间配置下的所有空间实体，支持分页和筛选"
)
async def list_spatial_entities(
    config_id: UUID,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=200, description="每页记录数"),
    entity_type: Optional[str] = Query(None, description="空间实体类型筛选"),
    parent_id: Optional[UUID] = Query(None, description="父级空间ID筛选"),
    search: Optional[str] = Query(None, description="搜索关键词（名称或编码）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间实体列表"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.list_spatial_entities(
            tenant_id=current_user.tenant_id,
            config_id=config_id,
            skip=skip,
            limit=limit,
            entity_type=entity_type,
            parent_id=parent_id,
            search=search
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间实体列表失败: {str(e)}"
        )

@router.get(
    "/entities/{entity_id}",
    response_model=SpatialEntityDTO,
    summary="获取空间实体详情",
    description="根据实体ID获取空间实体的详细信息"
)
async def get_spatial_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间实体详情"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.get_spatial_entity(
            tenant_id=current_user.tenant_id,
            entity_id=entity_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间实体不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间实体详情失败: {str(e)}"
        )

@router.put(
    "/entities/{entity_id}",
    response_model=SpatialEntityDTO,
    summary="更新空间实体",
    description="更新指定的空间实体信息"
)
async def update_spatial_entity(
    entity_id: UUID,
    spatial_entity: SpatialEntityDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新空间实体"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.update_spatial_entity(
            tenant_id=current_user.tenant_id,
            entity_id=entity_id,
            spatial_entity=spatial_entity,
            updated_by=current_user.username
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间实体不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新空间实体失败: {str(e)}"
        )

@router.delete(
    "/entities/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除空间实体",
    description="软删除指定的空间实体"
)
async def delete_spatial_entity(
    entity_id: UUID,
    force: bool = Query(False, description="是否强制删除（包括子级实体）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除空间实体"""
    service = SpatialConfigurationService(db)
    
    try:
        success = await service.delete_spatial_entity(
            tenant_id=current_user.tenant_id,
            entity_id=entity_id,
            force=force
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间实体不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除空间实体失败: {str(e)}"
        )

@router.get(
    "/entities/{entity_id}/children",
    response_model=List[SpatialEntityDTO],
    summary="获取子级空间实体",
    description="获取指定空间实体的所有直接子级实体"
)
async def get_spatial_entity_children(
    entity_id: UUID,
    include_inactive: bool = Query(False, description="是否包含非激活的实体"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取子级空间实体"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.get_spatial_entity_children(
            tenant_id=current_user.tenant_id,
            entity_id=entity_id,
            include_inactive=include_inactive
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取子级空间实体失败: {str(e)}"
        )

@router.get(
    "/entities/{entity_id}/path",
    response_model=List[SpatialEntityDTO],
    summary="获取空间实体路径",
    description="获取从根节点到指定空间实体的完整路径"
)
async def get_spatial_entity_path(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取空间实体路径"""
    service = SpatialConfigurationService(db)
    
    try:
        result = await service.get_spatial_entity_path(
            tenant_id=current_user.tenant_id,
            entity_id=entity_id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="空间实体不存在"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取空间实体路径失败: {str(e)}"
        )

@router.get(
    "/search",
    response_model=List[SpatialEntityDTO],
    summary="搜索空间实体",
    description="根据关键词搜索空间实体，支持名称、编码等字段搜索"
)
async def search_spatial_entities(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    entity_types: Optional[str] = Query(None, description="空间实体类型过滤，多个用逗号分隔"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量限制"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索空间实体"""
    service = SpatialConfigurationService(db)
    
    try:
        # 解析实体类型过滤
        entity_type_list = None
        if entity_types:
            entity_type_list = [t.strip() for t in entity_types.split(",")]
        
        result = await service.search_spatial_entities(
            tenant_id=current_user.tenant_id,
            query=query,
            entity_types=entity_type_list,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索空间实体失败: {str(e)}"
        ) 