"""
空间配置服务
提供空间配置管理的业务逻辑
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.application.interfaces.repository import (
    ISpatialConfigurationRepository,
    ISpatialEntityRepository
)
from app.domain.exceptions.config_exceptions import (
    SpatialConfigurationException,
    ConfigurationNotFoundException,
    DuplicateConfigurationException
)
from app.infrastructure.database.models import SpatialConfiguration, SpatialEntity
from app.core.logging import LoggerMixin


class SpatialConfigurationService(LoggerMixin):
    """空间配置服务"""
    
    def __init__(
        self,
        spatial_config_repository: ISpatialConfigurationRepository,
        spatial_entity_repository: ISpatialEntityRepository
    ):
        self.spatial_config_repo = spatial_config_repository
        self.spatial_entity_repo = spatial_entity_repository
        self.logger.info("空间配置服务初始化完成")
    
    async def get_spatial_configuration(
        self,
        config_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """获取空间配置详情"""
        try:
            config = await self.spatial_config_repo.get_by_id(config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("空间配置", str(config_id))
            
            # 获取关联的空间实体
            entities = await self.spatial_entity_repo.find_by_config(config_id)
            
            return {
                "id": config.id,
                "config_name": config.config_name,
                "config_version": config.config_version,
                "description": config.description,
                "spatial_schema": config.spatial_schema,
                "is_active": config.is_active,
                "entity_count": len(entities),
                "created_at": config.created_at,
                "updated_at": config.updated_at
            }
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"获取空间配置失败: {str(e)}")
            raise SpatialConfigurationException(f"获取空间配置失败: {str(e)}")
    
    async def get_spatial_hierarchy(
        self,
        config_id: UUID,
        tenant_id: str,
        root_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """获取空间层级结构"""
        try:
            config = await self.spatial_config_repo.get_by_id(config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("空间配置", str(config_id))
            
            # 获取层级树
            entities = await self.spatial_entity_repo.find_hierarchy_tree(root_id, UUID(tenant_id))
            
            hierarchy = []
            for entity in entities:
                hierarchy.append({
                    "id": entity.id,
                    "entity_code": entity.entity_code,
                    "entity_name": entity.entity_name,
                    "spatial_type": entity.spatial_type,
                    "level": entity.level,
                    "parent_id": entity.parent_id,
                    "operating_status": entity.operating_status,
                    "coordinates": entity.coordinates,
                    "properties": entity.properties
                })
            
            return hierarchy
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"获取空间层级结构失败: {str(e)}")
            raise SpatialConfigurationException(f"获取空间层级结构失败: {str(e)}")
    
    async def search_spatial_entities(
        self,
        tenant_id: str,
        spatial_type: Optional[str] = None,
        operating_status: Optional[str] = None,
        level: Optional[int] = None,
        search_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索空间实体"""
        try:
            entities = []
            
            if spatial_type:
                spatial_entities = await self.spatial_entity_repo.find_by_spatial_type(
                    spatial_type, UUID(tenant_id)
                )
                entities.extend(spatial_entities)
            elif operating_status:
                status_entities = await self.spatial_entity_repo.find_by_operating_status(
                    operating_status, UUID(tenant_id)
                )
                entities.extend(status_entities)
            elif level is not None:
                level_entities = await self.spatial_entity_repo.find_by_level(
                    level, UUID(tenant_id)
                )
                entities.extend(level_entities)
            else:
                # 获取所有实体
                all_entities = await self.spatial_entity_repo.find_by({
                    "tenant_id": UUID(tenant_id)
                })
                entities.extend(all_entities)
            
            # 文本搜索过滤
            if search_text:
                search_text = search_text.lower()
                entities = [
                    entity for entity in entities
                    if search_text in entity.entity_name.lower() or
                    search_text in entity.entity_code.lower()
                ]
            
            result = []
            for entity in entities:
                result.append({
                    "id": entity.id,
                    "entity_code": entity.entity_code,
                    "entity_name": entity.entity_name,
                    "spatial_type": entity.spatial_type,
                    "level": entity.level,
                    "operating_status": entity.operating_status,
                    "coordinates": entity.coordinates,
                    "properties": entity.properties
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"搜索空间实体失败: {str(e)}")
            raise SpatialConfigurationException(f"搜索空间实体失败: {str(e)}") 