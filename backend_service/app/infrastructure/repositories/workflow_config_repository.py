"""
工作流配置数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.application.interfaces.repository import IWorkflowConfigurationRepository, IWorkflowExecutionRepository
from app.infrastructure.database.models import WorkflowConfiguration, WorkflowExecution
from app.infrastructure.repositories.base_repository import BaseRepository


class WorkflowConfigurationRepository(BaseRepository[WorkflowConfiguration], IWorkflowConfigurationRepository):
    """工作流配置数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(WorkflowConfiguration, session)
    
    async def find_by_workflow_type(self, workflow_type: str, tenant_id: UUID) -> List[WorkflowConfiguration]:
        """根据工作流类型查找配置"""
        stmt = select(self.model).where(
            and_(
                self.model.workflow_type == workflow_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.workflow_version.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_active_by_type(self, workflow_type: str, tenant_id: UUID) -> List[WorkflowConfiguration]:
        """查找指定类型的活跃工作流配置"""
        stmt = select(self.model).where(
            and_(
                self.model.workflow_type == workflow_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.priority.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_name(self, workflow_name: str, tenant_id: UUID) -> Optional[WorkflowConfiguration]:
        """根据工作流名称查找配置"""
        stmt = select(self.model).where(
            and_(
                self.model.workflow_name == workflow_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_by_priority(self, priority: int, tenant_id: UUID) -> List[WorkflowConfiguration]:
        """根据优先级查找工作流配置"""
        stmt = select(self.model).where(
            and_(
                self.model.priority == priority,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_latest_version(self, workflow_type: str, tenant_id: UUID) -> int:
        """获取指定工作流类型的最新版本号"""
        stmt = select(func.max(self.model.workflow_version)).where(
            and_(
                self.model.workflow_type == workflow_type,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        max_version = result.scalar()
        return max_version or 0


class WorkflowExecutionRepository(BaseRepository[WorkflowExecution], IWorkflowExecutionRepository):
    """工作流执行数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(WorkflowExecution, session)
    
    async def find_by_config(self, workflow_config_id: UUID) -> List[WorkflowExecution]:
        """根据工作流配置ID查找执行记录"""
        stmt = select(self.model).where(
            self.model.workflow_configuration_id == workflow_config_id
        ).order_by(self.model.created_at.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_target_entity(
        self, 
        target_entity_type: str, 
        target_entity_id: str, 
        tenant_id: UUID
    ) -> List[WorkflowExecution]:
        """根据目标实体查找执行记录"""
        stmt = select(self.model).where(
            and_(
                self.model.target_entity_type == target_entity_type,
                self.model.target_entity_id == target_entity_id,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.created_at.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_status(self, status: str, tenant_id: UUID) -> List[WorkflowExecution]:
        """根据状态查找执行记录"""
        stmt = select(self.model).where(
            and_(
                self.model.execution_status == status,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.created_at.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_pending_executions(self, tenant_id: UUID) -> List[WorkflowExecution]:
        """查找待执行的工作流"""
        stmt = select(self.model).where(
            and_(
                self.model.execution_status.in_(['pending', 'running']),
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.created_at.asc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_timeout_executions(self, tenant_id: UUID) -> List[WorkflowExecution]:
        """查找超时的工作流执行"""
        from datetime import datetime, timedelta
        
        timeout_threshold = datetime.utcnow() - timedelta(hours=24)  # 24小时超时
        
        stmt = select(self.model).where(
            and_(
                self.model.execution_status == 'running',
                self.model.tenant_id == str(tenant_id),
                self.model.created_at < timeout_threshold
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all() 