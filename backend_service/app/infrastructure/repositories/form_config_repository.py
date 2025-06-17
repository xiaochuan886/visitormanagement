"""
表单配置数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.application.interfaces.repository import IFormConfigurationRepository, IFormFieldConfigurationRepository
from app.infrastructure.database.models import FormConfiguration, FormFieldConfiguration
from app.infrastructure.repositories.base_repository import BaseRepository


class FormConfigurationRepository(BaseRepository[FormConfiguration], IFormConfigurationRepository):
    """表单配置数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(FormConfiguration, session)
    
    async def find_by_form_type(self, form_type: str, tenant_id: UUID) -> List[FormConfiguration]:
        """根据表单类型查找配置"""
        stmt = select(self.model).where(
            and_(
                self.model.form_type == form_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.form_version.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_active_by_form_type(self, form_type: str, tenant_id: UUID) -> Optional[FormConfiguration]:
        """查找指定类型的活跃表单配置"""
        stmt = select(self.model).where(
            and_(
                self.model.form_type == form_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.form_version.desc()).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_default_by_form_type(self, form_type: str, tenant_id: UUID) -> Optional[FormConfiguration]:
        """查找指定类型的默认表单配置"""
        stmt = select(self.model).where(
            and_(
                self.model.form_type == form_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True,
                self.model.is_default == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_by_name(self, form_name: str, tenant_id: UUID) -> Optional[FormConfiguration]:
        """根据表单名称查找配置"""
        stmt = select(self.model).where(
            and_(
                self.model.form_name == form_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_latest_version(self, form_type: str, tenant_id: UUID) -> int:
        """获取指定表单类型的最新版本号"""
        stmt = select(func.max(self.model.form_version)).where(
            and_(
                self.model.form_type == form_type,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        max_version = result.scalar()
        return max_version or 0


class FormFieldConfigurationRepository(BaseRepository[FormFieldConfiguration], IFormFieldConfigurationRepository):
    """表单字段配置数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(FormFieldConfiguration, session)
    
    async def find_by_form_config(self, form_config_id: UUID) -> List[FormFieldConfiguration]:
        """根据表单配置ID查找字段列表"""
        stmt = select(self.model).where(
            self.model.form_configuration_id == form_config_id
        ).order_by(self.model.field_order)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_field_key(self, form_config_id: UUID, field_key: str) -> Optional[FormFieldConfiguration]:
        """根据字段键名查找字段配置"""
        stmt = select(self.model).where(
            and_(
                self.model.form_configuration_id == form_config_id,
                self.model.field_key == field_key
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def delete_by_form_config(self, form_config_id: UUID) -> bool:
        """删除指定表单配置的所有字段"""
        try:
            stmt = select(self.model).where(
                self.model.form_configuration_id == form_config_id
            )
            result = await self.session.execute(stmt)
            fields = result.scalars().all()
            
            for field in fields:
                await self.session.delete(field)
            
            await self.session.commit()
            return True
        except Exception:
            await self.session.rollback()
            return False 