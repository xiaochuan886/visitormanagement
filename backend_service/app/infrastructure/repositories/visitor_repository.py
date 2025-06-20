"""
访客数据访问实现
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.visitor import Visitor
from app.domain.base_enums import VisitorStatus
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
                tenant_id=entity.tenant_id,
                pass_code=getattr(entity, 'pass_code', None),
                name=entity.name,
                email=getattr(entity, 'email', None),
                phone_number=getattr(entity, 'phone_number', None),
                identification_no=getattr(entity, 'identification_no', None),
                license_plate_number=getattr(entity, 'license_plate_number', None),
                address=getattr(entity, 'address', None),
                gender=getattr(entity, 'gender', None),
                company_name=getattr(entity, 'company_name', None),
                purpose=getattr(entity, 'purpose', None),
                comment=getattr(entity, 'comment', None),
                designation_id=getattr(entity, 'designation_id', None),
                employee_id=getattr(entity, 'employee_id', None),
                checkin_date=getattr(entity, 'checkin_date', None),
                checkout_date=getattr(entity, 'checkout_date', None),
                expected_date=getattr(entity, 'expected_date', None),
                expected_time=getattr(entity, 'expected_time', None),
                avatar=getattr(entity, 'avatar', None),
                trip_code=getattr(entity, 'trip_code', None),
                health_code=getattr(entity, 'health_code', None),
                qr_code=getattr(entity, 'qr_code', None),
                nucleic_acid_test_report=getattr(entity, 'nucleic_acid_test_report', None),
                privacy_policy=getattr(entity, 'privacy_policy', None),
                promise=getattr(entity, 'promise', None),
                status=getattr(entity, 'status', 'pending'),
                approved=getattr(entity, 'approved', None),
                approval_outcome=getattr(entity, 'approval_outcome', None),
                approval_comment=getattr(entity, 'approval_comment', None),
                site_id=getattr(entity, 'site_id', None),
                survey_response_value=getattr(entity, 'survey_response_value', None),
                # 门岗前台字段设置默认值
                current_status=getattr(entity, 'current_status', None),
                entry_time=getattr(entity, 'entry_time', None),
                exit_time=getattr(entity, 'exit_time', None),
                current_location=getattr(entity, 'current_location', None),
                reception_desk_id=getattr(entity, 'reception_desk_id', None),
                # 基础字段
                is_active=getattr(entity, 'is_active', True),
                created_by=getattr(entity, 'created_by', None),
                updated_by=getattr(entity, 'updated_by', None)
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
            
            # 更新字段 - 使用正确的字段名
            model.pass_code = entity.pass_code
            model.name = entity.name
            model.email = entity.email
            model.phone_number = entity.phone_number
            model.identification_no = entity.identification_no
            model.license_plate_number = entity.license_plate_number
            model.address = entity.address
            model.gender = entity.gender
            model.company_name = entity.company_name
            model.purpose = entity.purpose
            model.comment = entity.comment
            model.designation_id = entity.designation_id
            model.employee_id = entity.employee_id
            model.checkin_date = entity.checkin_date
            model.checkout_date = entity.checkout_date
            model.expected_date = entity.expected_date
            model.expected_time = entity.expected_time
            model.avatar = entity.avatar
            model.trip_code = entity.trip_code
            model.health_code = entity.health_code
            model.qr_code = entity.qr_code
            model.nucleic_acid_test_report = entity.nucleic_acid_test_report
            model.privacy_policy = entity.privacy_policy
            model.promise = entity.promise
            model.status = entity.status
            model.approved = entity.approved
            model.approval_outcome = entity.approval_outcome
            model.approval_comment = entity.approval_comment
            model.site_id = entity.site_id
            model.survey_response_value = entity.survey_response_value
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
            model.updated_by = entity.updated_by
            
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
                        VisitorModel.phone_number == phone,
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
                        VisitorModel.identification_no == id_card,
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
        """查找活跃访问"""
        try:
            result = await self.session.execute(
                select(VisitorModel).where(
                    and_(
                        VisitorModel.tenant_id == tenant_id,
                        VisitorModel.status.in_([
                            VisitorStatus.APPROVED,
                            VisitorStatus.CHECKED_IN
                        ])
                    )
                ).order_by(VisitorModel.checkin_date.desc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"查找活跃访问失败: {str(e)}")
            raise
    
    async def find_by_employee(self, employee_id: UUID, tenant_id: UUID) -> List[Visitor]:
        """根据员工查找访客"""
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
                        VisitorModel.expected_date >= start_date,
                        VisitorModel.expected_date <= end_date
                    )
                ).order_by(VisitorModel.expected_date.asc())
            )
            models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in models]
            
        except Exception as e:
            self.logger.error(f"根据日期范围查找访客失败: {str(e)}")
            raise
    
    def _model_to_entity(self, model: VisitorModel) -> Visitor:
        """将模型转换为实体 - 修复字段映射"""
        return Visitor(
            id=model.id,
            tenant_id=model.tenant_id,
            pass_code=model.pass_code,
            name=model.name,
            email=model.email,
            phone_number=model.phone_number,
            identification_no=model.identification_no,
            license_plate_number=model.license_plate_number,
            address=model.address,
            gender=model.gender,
            company_name=model.company_name,
            purpose=model.purpose,
            comment=model.comment,
            designation_id=model.designation_id,
            employee_id=model.employee_id,
            checkin_date=model.checkin_date,
            checkout_date=model.checkout_date,
            expected_date=model.expected_date,
            expected_time=model.expected_time,
            avatar=model.avatar,
            trip_code=model.trip_code,
            health_code=model.health_code,
            qr_code=model.qr_code,
            nucleic_acid_test_report=model.nucleic_acid_test_report,
            privacy_policy=model.privacy_policy,
            promise=model.promise,
            status=model.status,
            approved=model.approved,
            approval_outcome=model.approval_outcome,
            approval_comment=model.approval_comment,
            site_id=model.site_id,
            survey_response_value=model.survey_response_value,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            updated_by=model.updated_by
        ) 