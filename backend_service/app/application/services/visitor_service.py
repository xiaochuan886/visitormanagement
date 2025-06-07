"""
访客服务层
"""
import uuid
import qrcode
from io import BytesIO
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import VisitorModel, EmployeeModel, SiteModel
from app.application.dto.visitor_dto import (
    VisitorCreateDTO,
    VisitorUpdateDTO,
    VisitorResponseDTO,
    VisitorListResponseDTO,
    VisitorApprovalDTO,
    VisitorCheckinDTO,
    VisitorCheckoutDTO,
    VisitorQueryDTO
)
from app.domain.enums import VisitorStatus, ApprovalOutcome
from app.infrastructure.cache.redis_client import get_redis
from app.core.config import settings


class VisitorService:
    """访客服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_visitor(
        self, 
        visitor_data: VisitorCreateDTO, 
        created_by: str, 
        tenant_id: str
    ) -> VisitorResponseDTO:
        """创建访客"""
        # 生成通行码
        pass_code = self._generate_pass_code()
        
        # 创建访客模型
        visitor = VisitorModel(
            pass_code=pass_code,
            name=visitor_data.name,
            email=visitor_data.email,
            phone_number=visitor_data.phone_number,
            identification_no=visitor_data.identification_no,
            license_plate_number=visitor_data.license_plate_number,
            address=visitor_data.address,
            gender=visitor_data.gender,
            company_name=visitor_data.company_name,
            purpose=visitor_data.purpose,
            comment=visitor_data.comment,
            employee_id=visitor_data.employee_id,
            expected_date=visitor_data.expected_date,
            expected_time=visitor_data.expected_time,
            privacy_policy=visitor_data.privacy_policy,
            promise=visitor_data.promise,
            site_id=visitor_data.site_id,
            status=VisitorStatus.PENDING,
            tenant_id=tenant_id,
            created_by=created_by
        )
        
        self.db.add(visitor)
        await self.db.commit()
        await self.db.refresh(visitor)
        
        # 缓存访客信息
        await self._cache_visitor(visitor)
        
        return VisitorResponseDTO.from_orm(visitor)
    
    async def get_visitors(
        self, 
        query: VisitorQueryDTO, 
        tenant_id: str
    ) -> VisitorListResponseDTO:
        """获取访客列表"""
        # 构建查询条件
        conditions = [VisitorModel.tenant_id == tenant_id, VisitorModel.is_deleted == False]
        
        if query.name:
            conditions.append(VisitorModel.name.ilike(f"%{query.name}%"))
        if query.phone_number:
            conditions.append(VisitorModel.phone_number.ilike(f"%{query.phone_number}%"))
        if query.email:
            conditions.append(VisitorModel.email.ilike(f"%{query.email}%"))
        if query.status:
            conditions.append(VisitorModel.status == query.status)
        if query.employee_id:
            conditions.append(VisitorModel.employee_id == query.employee_id)
        if query.site_id:
            conditions.append(VisitorModel.site_id == query.site_id)
        if query.start_date:
            conditions.append(VisitorModel.created_at >= query.start_date)
        if query.end_date:
            conditions.append(VisitorModel.created_at <= query.end_date)
        
        # 查询总数
        count_stmt = select(func.count(VisitorModel.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (query.page - 1) * query.page_size
        stmt = (
            select(VisitorModel)
            .where(and_(*conditions))
            .options(
                selectinload(VisitorModel.employee),
                selectinload(VisitorModel.site)
            )
            .offset(offset)
            .limit(query.page_size)
            .order_by(VisitorModel.created_at.desc())
        )
        
        result = await self.db.execute(stmt)
        visitors = result.scalars().all()
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size
        
        return VisitorListResponseDTO(
            items=[VisitorResponseDTO.from_orm(visitor) for visitor in visitors],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    async def get_visitor_by_id(
        self, 
        visitor_id: int, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """根据ID获取访客"""
        # 先尝试从缓存获取
        cached_visitor = await self._get_cached_visitor(visitor_id, tenant_id)
        if cached_visitor:
            return cached_visitor
        
        # 从数据库查询
        stmt = (
            select(VisitorModel)
            .where(
                and_(
                    VisitorModel.id == visitor_id,
                    VisitorModel.tenant_id == tenant_id,
                    VisitorModel.is_deleted == False
                )
            )
            .options(
                selectinload(VisitorModel.employee),
                selectinload(VisitorModel.site)
            )
        )
        
        result = await self.db.execute(stmt)
        visitor = result.scalar_one_or_none()
        
        if visitor:
            # 缓存访客信息
            await self._cache_visitor(visitor)
            return VisitorResponseDTO.from_orm(visitor)
        
        return None
    
    async def update_visitor(
        self, 
        visitor_id: int, 
        visitor_data: VisitorUpdateDTO, 
        updated_by: str, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """更新访客信息"""
        # 获取访客
        stmt = (
            select(VisitorModel)
            .where(
                and_(
                    VisitorModel.id == visitor_id,
                    VisitorModel.tenant_id == tenant_id,
                    VisitorModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        visitor = result.scalar_one_or_none()
        
        if not visitor:
            return None
        
        # 更新字段
        update_data = visitor_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(visitor, field, value)
        
        visitor.updated_by = updated_by
        visitor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(visitor)
        
        # 更新缓存
        await self._cache_visitor(visitor)
        
        return VisitorResponseDTO.from_orm(visitor)
    
    async def delete_visitor(
        self, 
        visitor_id: int, 
        deleted_by: str, 
        tenant_id: str
    ) -> bool:
        """删除访客（软删除）"""
        stmt = (
            select(VisitorModel)
            .where(
                and_(
                    VisitorModel.id == visitor_id,
                    VisitorModel.tenant_id == tenant_id,
                    VisitorModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        visitor = result.scalar_one_or_none()
        
        if not visitor:
            return False
        
        # 软删除
        visitor.is_deleted = True
        visitor.deleted_by = deleted_by
        visitor.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        
        # 清除缓存
        await self._clear_visitor_cache(visitor_id, tenant_id)
        
        return True
    
    async def approve_visitor(
        self, 
        visitor_id: int, 
        approval_data: VisitorApprovalDTO, 
        approver: str, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """审批访客"""
        visitor = await self._get_visitor_model(visitor_id, tenant_id)
        if not visitor:
            return None
        
        # 更新审批信息
        visitor.approval_outcome = approval_data.approval_outcome
        visitor.approval_comment = approval_data.approval_comment
        visitor.approved = approval_data.approval_outcome == ApprovalOutcome.APPROVED
        visitor.updated_by = approver
        visitor.updated_at = datetime.utcnow()
        
        # 更新状态
        if approval_data.approval_outcome == ApprovalOutcome.APPROVED:
            visitor.status = VisitorStatus.APPROVED
        else:
            visitor.status = VisitorStatus.REJECTED
        
        await self.db.commit()
        await self.db.refresh(visitor)
        
        # 更新缓存
        await self._cache_visitor(visitor)
        
        return VisitorResponseDTO.from_orm(visitor)
    
    async def checkin_visitor(
        self, 
        visitor_id: int, 
        checkin_data: VisitorCheckinDTO, 
        operator: str, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """访客签到"""
        visitor = await self._get_visitor_model(visitor_id, tenant_id)
        if not visitor or visitor.status != VisitorStatus.APPROVED:
            return None
        
        # 签到
        visitor.checkin_date = datetime.utcnow()
        visitor.status = VisitorStatus.CHECKED_IN
        visitor.updated_by = operator
        visitor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(visitor)
        
        # 更新缓存
        await self._cache_visitor(visitor)
        
        return VisitorResponseDTO.from_orm(visitor)
    
    async def checkout_visitor(
        self, 
        visitor_id: int, 
        checkout_data: VisitorCheckoutDTO, 
        operator: str, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """访客签出"""
        visitor = await self._get_visitor_model(visitor_id, tenant_id)
        if not visitor or visitor.status != VisitorStatus.CHECKED_IN:
            return None
        
        # 签出
        visitor.checkout_date = datetime.utcnow()
        visitor.status = VisitorStatus.CHECKED_OUT
        visitor.updated_by = operator
        visitor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(visitor)
        
        # 更新缓存
        await self._cache_visitor(visitor)
        
        return VisitorResponseDTO.from_orm(visitor)
    
    async def generate_visitor_qrcode(
        self, 
        visitor_id: int, 
        tenant_id: str
    ) -> Optional[str]:
        """生成访客二维码"""
        visitor = await self._get_visitor_model(visitor_id, tenant_id)
        if not visitor:
            return None
        
        # 生成二维码数据
        qr_data = {
            "visitor_id": visitor_id,
            "pass_code": visitor.pass_code,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 生成二维码
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        # 生成二维码图片（这里返回URL，实际项目中需要保存到文件系统）
        qr_code_url = f"/uploads/qrcodes/{visitor_id}_{visitor.pass_code}.png"
        
        # 更新访客二维码字段
        visitor.qr_code = qr_code_url
        await self.db.commit()
        
        return qr_code_url
    
    def _generate_pass_code(self) -> str:
        """生成通行码"""
        return str(uuid.uuid4()).replace("-", "")[:8].upper()
    
    async def _get_visitor_model(
        self, 
        visitor_id: int, 
        tenant_id: str
    ) -> Optional[VisitorModel]:
        """获取访客模型"""
        stmt = (
            select(VisitorModel)
            .where(
                and_(
                    VisitorModel.id == visitor_id,
                    VisitorModel.tenant_id == tenant_id,
                    VisitorModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _cache_visitor(self, visitor: VisitorModel) -> None:
        """缓存访客信息"""
        try:
            redis_client = await get_redis()
            cache_key = f"visitor:{visitor.tenant_id}:{visitor.id}"
            visitor_data = VisitorResponseDTO.from_orm(visitor).dict()
            await redis_client.set(cache_key, visitor_data, expire=3600)  # 1小时过期
        except Exception as e:
            print(f"缓存访客信息失败: {e}")
    
    async def _get_cached_visitor(
        self, 
        visitor_id: int, 
        tenant_id: str
    ) -> Optional[VisitorResponseDTO]:
        """从缓存获取访客信息"""
        try:
            redis_client = await get_redis()
            cache_key = f"visitor:{tenant_id}:{visitor_id}"
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return VisitorResponseDTO(**cached_data)
        except Exception as e:
            print(f"从缓存获取访客信息失败: {e}")
        return None
    
    async def _clear_visitor_cache(self, visitor_id: int, tenant_id: str) -> None:
        """清除访客缓存"""
        try:
            redis_client = await get_redis()
            cache_key = f"visitor:{tenant_id}:{visitor_id}"
            await redis_client.delete(cache_key)
        except Exception as e:
            print(f"清除访客缓存失败: {e}") 