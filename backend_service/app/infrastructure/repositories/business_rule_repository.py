"""
业务规则数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.application.interfaces.repository import IBusinessRuleRepository, IRuleExecutionLogRepository
from app.infrastructure.database.models import BusinessRule, RuleExecutionLog
from app.infrastructure.repositories.base_repository import BaseRepository


class BusinessRuleRepository(BaseRepository[BusinessRule], IBusinessRuleRepository):
    """业务规则数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(BusinessRule, session)
    
    async def find_by_category(self, rule_category: str, tenant_id: UUID) -> List[BusinessRule]:
        """根据规则类别查找"""
        stmt = select(self.model).where(
            and_(
                self.model.rule_category == rule_category,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.priority.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_active_rules(self, tenant_id: UUID) -> List[BusinessRule]:
        """查找活跃的业务规则"""
        stmt = select(self.model).where(
            and_(
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.priority.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_target_entity(self, target_entity_type: str, tenant_id: UUID) -> List[BusinessRule]:
        """根据目标实体类型查找规则"""
        stmt = select(self.model).where(
            and_(
                self.model.target_entity_type == target_entity_type,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        ).order_by(self.model.priority.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_priority(self, priority: int, tenant_id: UUID) -> List[BusinessRule]:
        """根据优先级查找规则"""
        stmt = select(self.model).where(
            and_(
                self.model.priority == priority,
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_name(self, rule_name: str, tenant_id: UUID) -> Optional[BusinessRule]:
        """根据规则名称查找"""
        stmt = select(self.model).where(
            and_(
                self.model.rule_name == rule_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def find_effective_rules(self, effective_date: Any, tenant_id: UUID) -> List[BusinessRule]:
        """查找在指定日期有效的规则"""
        stmt = select(self.model).where(
            and_(
                self.model.tenant_id == str(tenant_id),
                self.model.is_active == True,
                or_(
                    self.model.effective_start_date.is_(None),
                    self.model.effective_start_date <= effective_date
                ),
                or_(
                    self.model.effective_end_date.is_(None),
                    self.model.effective_end_date >= effective_date
                )
            )
        ).order_by(self.model.priority.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_latest_version(self, rule_name: str, tenant_id: UUID) -> int:
        """获取指定规则的最新版本号"""
        stmt = select(func.max(self.model.rule_version)).where(
            and_(
                self.model.rule_name == rule_name,
                self.model.tenant_id == str(tenant_id)
            )
        )
        
        result = await self.session.execute(stmt)
        max_version = result.scalar()
        return max_version or 0


class RuleExecutionLogRepository(BaseRepository[RuleExecutionLog], IRuleExecutionLogRepository):
    """规则执行日志数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(RuleExecutionLog, session)
    
    async def find_by_rule(self, rule_id: UUID) -> List[RuleExecutionLog]:
        """根据规则ID查找执行日志"""
        stmt = select(self.model).where(
            self.model.business_rule_id == rule_id
        ).order_by(self.model.execution_timestamp.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_target_entity(
        self, 
        target_entity_type: str, 
        target_entity_id: str, 
        tenant_id: UUID
    ) -> List[RuleExecutionLog]:
        """根据目标实体查找执行日志"""
        stmt = select(self.model).where(
            and_(
                self.model.target_entity_type == target_entity_type,
                self.model.target_entity_id == target_entity_id,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.execution_timestamp.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_execution_result(self, result: str, tenant_id: UUID) -> List[RuleExecutionLog]:
        """根据执行结果查找日志"""
        stmt = select(self.model).where(
            and_(
                self.model.execution_result == result,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.execution_timestamp.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def find_by_date_range(
        self, 
        start_date: Any, 
        end_date: Any, 
        tenant_id: UUID
    ) -> List[RuleExecutionLog]:
        """根据日期范围查找执行日志"""
        stmt = select(self.model).where(
            and_(
                self.model.execution_timestamp >= start_date,
                self.model.execution_timestamp <= end_date,
                self.model.tenant_id == str(tenant_id)
            )
        ).order_by(self.model.execution_timestamp.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_execution_statistics(
        self, 
        rule_id: UUID, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取规则执行统计信息"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 总执行次数
        total_stmt = select(func.count(self.model.id)).where(
            and_(
                self.model.business_rule_id == rule_id,
                self.model.execution_timestamp >= start_date
            )
        )
        total_result = await self.session.execute(total_stmt)
        total_executions = total_result.scalar() or 0
        
        # 成功执行次数
        success_stmt = select(func.count(self.model.id)).where(
            and_(
                self.model.business_rule_id == rule_id,
                self.model.execution_result == 'success',
                self.model.execution_timestamp >= start_date
            )
        )
        success_result = await self.session.execute(success_stmt)
        success_executions = success_result.scalar() or 0
        
        # 平均执行时间
        avg_time_stmt = select(func.avg(self.model.execution_duration_ms)).where(
            and_(
                self.model.business_rule_id == rule_id,
                self.model.execution_timestamp >= start_date
            )
        )
        avg_time_result = await self.session.execute(avg_time_stmt)
        avg_execution_time = avg_time_result.scalar() or 0
        
        return {
            "total_executions": total_executions,
            "success_executions": success_executions,
            "success_rate": success_executions / total_executions if total_executions > 0 else 0,
            "avg_execution_time_ms": float(avg_execution_time),
            "period_days": days
        } 