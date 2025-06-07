"""
访客数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.visitor import Visitor
from app.domain.enums import VisitStatus
from app.application.interfaces.repository import IVisitorRepository
from app.infrastructure.database.models import VisitorModel
from app.core.logging import LoggerMixin


class VisitorRepository(IVisitorRepository[Visitor], LoggerMixin):
    """访客数据访问实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, entity: Visitor) -> Visitor:
        """创建访客"""
        try:
            model = VisitorModel(
                id=entity.id,
                tenant_id=entity.tenant_id,
                name=entity.name,
                phone=entity.phone,
                id_card=entity.id_card,
                company=entity.company,
                purpose=entity.purpose,
                employee_id=entity.employee_id,
                department_id=entity.department_id,
                site_id=entity.site_id,
                visit_date=entity.visit_date,
                status=entity.status,
                check_in_time=entity.check_in_time,
                check_out_time=entity.check_out_time,
                qr_code=entity.qr_code,
                photo_url=entity.photo_url,
                notes=entity.notes,
                is_active=entity.is_active,
                created_at=entity.created_at,
                updated_at=entity.updated_at
            )
            
            self.session.add(model)
            await self.session.flush()
            await self.session.refresh(model)
            
            self.logger.info(f"创建访客成功: {entity.id}")
            return self._model_to_entity(model)
            
        except Exception as e:
            self.logger.error(f"创建访客失败: {str(e)}")
            raise
    
    async def get_by_id(self, entity_id: UUID) -> Optional[Visitor]:
        """根据ID获取访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(VisitorModel.id == entity_id)
            )
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            self.logger.error(f"根据ID获取访客失败: {str(e)}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Visitor]:
        """获取所有访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel)
                .offset(skip)
                .limit(limit)
                .order_by(VisitorModel.created_at.desc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"获取所有访客失败: {str(e)}")
            raise
    
    async def update(self, entity: Visitor) -> Visitor:
        """更新访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(VisitorModel.id == entity.id)
            )
            model = result.scalar_one_or_none()
            
            if not model:
                raise ValueError(f"访客不存在: {entity.id}")
            
            # 更新字段
            model.name = entity.name
            model.phone = entity.phone
            model.id_card = entity.id_card
            model.company = entity.company
            model.purpose = entity.purpose
            model.employee_id = entity.employee_id
            model.department_id = entity.department_id
            model.site_id = entity.site_id
            model.visit_date = entity.visit_date
            model.status = entity.status
            model.check_in_time = entity.check_in_time
            model.check_out_time = entity.check_out_time
            model.qr_code = entity.qr_code
            model.photo_url = entity.photo_url
            model.notes = entity.notes
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
            
            await self.session.flush()
            await self.session.refresh(model)
            
            self.logger.info(f"更新访客成功: {entity.id}")
            return self._model_to_entity(model)
            
        except Exception as e:
            self.logger.error(f"更新访客失败: {str(e)}")
            raise
    
    async def delete(self, entity_id: UUID) -> bool:
        """删除访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(VisitorModel.id == entity_id)
            )
            model = result.scalar_one_or_none()
            
            if not model:
                return False
            
            await self.session.delete(model)
            self.logger.info(f"删除访客成功: {entity_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除访客失败: {str(e)}")
            raise
    
    async def find_by(self, filters: Dict[str, Any]) -> List[Visitor]:
        """根据条件查找访客"""
        try:
            query = select(VisitorModel)
            
            # 构建查询条件
            conditions = []
            for key, value in filters.items():
                if hasattr(VisitorModel, key) and value is not None:
                    conditions.append(getattr(VisitorModel, key) == value)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await self.session.execute(query.order_by(VisitorModel.created_at.desc()))
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"根据条件查找访客失败: {str(e)}")
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计访客数量"""
        try:
            query = select(func.count(VisitorModel.id))
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if hasattr(VisitorModel, key) and value is not None:
                        conditions.append(getattr(VisitorModel, key) == value)
                
                if conditions:
                    query = query.where(and_(*conditions))
            
            result = await self.session.execute(query)
            return result.scalar()
            
        except Exception as e:
            self.logger.error(f"统计访客数量失败: {str(e)}")
            raise
    
    async def find_by_phone(self, phone: str, tenant_id: UUID) -> Optional[Visitor]:
        """根据手机号查找访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.phone == phone,
                        VisitorModel.tenant_id == tenant_id
                    )
                )
            )
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            self.logger.error(f"根据手机号查找访客失败: {str(e)}")
            raise
    
    async def find_by_id_card(self, id_card: str, tenant_id: UUID) -> Optional[Visitor]:
        """根据身份证号查找访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.id_card == id_card,
                        VisitorModel.tenant_id == tenant_id
                    )
                )
            )
            model = result.scalar_one_or_none()
            
            if model:
                return self._model_to_entity(model)
            return None
            
        except Exception as e:
            self.logger.error(f"根据身份证号查找访客失败: {str(e)}")
            raise
    
    async def find_active_visits(self, tenant_id: UUID) -> List[Visitor]:
        """查找当前活跃的访问记录"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.tenant_id == tenant_id,
                        VisitorModel.status.in_([VisitStatus.CHECKED_IN, VisitStatus.APPROVED]),
                        VisitorModel.is_active == True
                    )
                ).order_by(VisitorModel.check_in_time.desc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"查找活跃访问记录失败: {str(e)}")
            raise
    
    async def find_by_employee(self, employee_id: UUID, tenant_id: UUID) -> List[Visitor]:
        """根据被访员工查找访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.employee_id == employee_id,
                        VisitorModel.tenant_id == tenant_id
                    )
                ).order_by(VisitorModel.created_at.desc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"根据员工查找访客失败: {str(e)}")
            raise
    
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        tenant_id: UUID
    ) -> List[Visitor]:
        """根据日期范围查找访客"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.tenant_id == tenant_id,
                        VisitorModel.visit_date >= start_date,
                        VisitorModel.visit_date <= end_date
                    )
                ).order_by(VisitorModel.visit_date.desc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"根据日期范围查找访客失败: {str(e)}")
            raise
    
    def _model_to_entity(self, model: VisitorModel) -> Visitor:
        """将数据模型转换为领域实体"""
        return Visitor(
            id=model.id,
            tenant_id=model.tenant_id,
            name=model.name,
            phone=model.phone,
            id_card=model.id_card,
            company=model.company,
            purpose=model.purpose,
            employee_id=model.employee_id,
            department_id=model.department_id,
            site_id=model.site_id,
            visit_date=model.visit_date,
            status=model.status,
            check_in_time=model.check_in_time,
            check_out_time=model.check_out_time,
            qr_code=model.qr_code,
            photo_url=model.photo_url,
            notes=model.notes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 