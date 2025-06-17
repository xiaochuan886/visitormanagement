"""
空间配置数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.application.interfaces.repository import ISpatialConfigurationRepository, ISpatialEntityRepository
from app.infrastructure.database.models import SpatialConfiguration, SpatialEntity
from app.infrastructure.repositories.base_repository import BaseRepository


class SpatialConfigurationRepository(BaseRepository[SpatialConfiguration], ISpatialConfigurationRepository):
    """空间配置数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(SpatialConfiguration, session)
    
    async def find_by_name(self, config_name: str, tenant_id: UUID) -> Optional[SpatialConfiguration]:
        """根据配置名称查找"""
        stmt = select(self.model).where(
            and_(
                self.model.config_name == config_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_active_configs(self, tenant_id: UUID) -> List[SpatialConfiguration]:
        """查找活跃的空间配置"""
        stmt = select(self.model).where(
            and_(
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.config_version.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_latest_version(self, config_name: str, tenant_id: UUID) -> int:
        """获取指定配置的最新版本号"""
        stmt = select(func.max(self.model.config_version)).where(
            and_(
                self.model.config_name == config_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        max_version = result.scalar()
        return max_version or 0


class SpatialEntityRepository(BaseRepository[SpatialEntity], ISpatialEntityRepository):
    """空间实体数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(SpatialEntity, session)
    
    async def find_by_config(self, spatial_config_id: UUID) -> List[SpatialEntity]:
        """根据空间配置ID查找实体"""
        stmt = select(self.model).where(
            self.model.spatial_configuration_id == spatial_config_id
        ).order_by(self.model.hierarchy_level, self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_entity_code(self, entity_code: str, tenant_id: UUID) -> Optional[SpatialEntity]:
        """根据实体编码查找"""
        stmt = select(self.model).where(
            and_(
                self.model.entity_code == entity_code,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_by_spatial_type(self, spatial_type: str, tenant_id: UUID) -> List[SpatialEntity]:
        """根据空间类型查找实体"""
        stmt = select(self.model).where(
            and_(
                self.model.spatial_type == spatial_type,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.hierarchy_level, self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_parent(self, parent_id: UUID) -> List[SpatialEntity]:
        """根据父级ID查找子实体"""
        stmt = select(self.model).where(
            self.model.parent_entity_id == parent_id
        ).order_by(self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_level(self, level: int, tenant_id: UUID) -> List[SpatialEntity]:
        """根据层级查找实体"""
        stmt = select(self.model).where(
            and_(
                self.model.hierarchy_level == level,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_hierarchy_tree(self, root_id: Optional[UUID], tenant_id: UUID) -> List[SpatialEntity]:
        """查找层级树结构"""
        if root_id:
            stmt = select(self.model).where(
                and_(
                    self.model.parent_entity_id == root_id,
                    self.model.tenant_id == str(tenant_id)
                )
            ).order_by(self.model.hierarchy_level, self.model.entity_order)
        else:
            # 查找顶级实体
            stmt = select(self.model).where(
                and_(
                    self.model.parent_entity_id.is_(None),
                    self.model.tenant_id == str(tenant_id)
                )
            ).order_by(self.model.hierarchy_level, self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_operating_status(self, status: str, tenant_id: UUID) -> List[SpatialEntity]:
        """根据运营状态查找实体"""
        stmt = select(self.model).where(
            and_(
                self.model.operating_status == status,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.hierarchy_level, self.model.entity_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all() 