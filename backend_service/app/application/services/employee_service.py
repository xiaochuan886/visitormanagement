"""
员工服务层 - 优化版本 v2.0
支持新的约束验证和数据完整性检查
"""
import re
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models import EmployeeModel, DepartmentModel
from app.application.dto.employee_dto import (
    EmployeeCreateDTO,
    EmployeeUpdateDTO,
    EmployeeResponseDTO,
    EmployeeListResponseDTO,
    EmployeeQueryDTO
)
from app.domain.base_enums import EmployeeStatus
from app.infrastructure.cache.redis_client import get_redis
from app.core.serializers import serialize_for_cache, deserialize_from_cache


class EmployeeService:
    """员工服务 - 优化版本"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        if not email:
            return True  # 允许空邮箱
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """验证电话号码格式"""
        if not phone:
            return True  # 允许空电话
        pattern = r'^[0-9+\-\s()]{10,20}$'
        return bool(re.match(pattern, phone))
    
    def _validate_gender(self, gender: str) -> bool:
        """验证性别"""
        if not gender:
            return True  # 允许空性别
        return gender in ['male', 'female', 'other']
    
    def _validate_status(self, status: str) -> bool:
        """验证员工状态"""
        if not status:
            return True
        return status in ['active', 'inactive', 'terminated', 'on_leave']
    
    def _validate_salary(self, salary: float) -> bool:
        """验证薪资"""
        if salary is None:
            return True  # 允许空薪资
        return salary >= 0
    
    async def create_employee(
        self, 
        employee_data: EmployeeCreateDTO, 
        created_by: str, 
        tenant_id: str
    ) -> EmployeeResponseDTO:
        """创建员工 - 增强验证版本"""
        # 数据验证
        if not self._validate_email(employee_data.email):
            raise ValueError(f"邮箱格式不正确: {employee_data.email}")
        
        if not self._validate_phone(employee_data.phone_number):
            raise ValueError(f"电话号码格式不正确: {employee_data.phone_number}")
        
        if not self._validate_phone(employee_data.emergency_phone):
            raise ValueError(f"紧急联系电话格式不正确: {employee_data.emergency_phone}")
        
        if not self._validate_gender(employee_data.gender):
            raise ValueError(f"性别值不正确: {employee_data.gender}")
        
        if not self._validate_status(employee_data.status):
            raise ValueError(f"员工状态不正确: {employee_data.status}")
        
        if not self._validate_salary(employee_data.salary):
            raise ValueError(f"薪资不能为负数: {employee_data.salary}")
        
        # 检查员工工号是否已存在
        existing_employee = await self._get_employee_by_employee_id(employee_data.employee_id, tenant_id)
        if existing_employee:
            raise ValueError(f"员工工号 {employee_data.employee_id} 已存在")
        
        # 检查邮箱是否已存在
        if employee_data.email:
            existing_email = await self._get_employee_by_email(employee_data.email, tenant_id)
            if existing_email:
                raise ValueError(f"邮箱 {employee_data.email} 已存在")
        
        # 验证部门是否存在
        department = await self._get_department_by_id(employee_data.department_id, tenant_id)
        if not department:
            raise ValueError(f"部门 {employee_data.department_id} 不存在")
        
        # 验证上级是否存在
        if employee_data.manager_id:
            manager = await self._get_employee_by_id_internal(employee_data.manager_id, tenant_id)
            if not manager:
                raise ValueError(f"上级员工 {employee_data.manager_id} 不存在")
        
        try:
            # 创建员工模型
            employee = EmployeeModel(
                name=employee_data.name,
                employee_id=employee_data.employee_id,
                email=employee_data.email,
                phone_number=employee_data.phone_number,
                department_id=employee_data.department_id,
                position=employee_data.position,
                manager_id=employee_data.manager_id,
                hire_date=employee_data.hire_date,
                birth_date=employee_data.birth_date,
                gender=employee_data.gender,
                address=employee_data.address,
                emergency_contact=employee_data.emergency_contact,
                emergency_phone=employee_data.emergency_phone,
                salary=employee_data.salary,
                status=employee_data.status or EmployeeStatus.ACTIVE,
                tenant_id=tenant_id,
                created_by=created_by
            )
            
            self.db.add(employee)
            await self.db.commit()
            await self.db.refresh(employee)
        except IntegrityError as e:
            await self.db.rollback()
            if "chk_employees_" in str(e):
                raise ValueError(f"数据验证失败: {str(e)}")
            elif "unique" in str(e).lower():
                raise ValueError(f"数据重复: {str(e)}")
            else:
                raise ValueError(f"数据库约束错误: {str(e)}")
        
        # 缓存员工信息 (暂时禁用)
        await self._cache_employee(employee)
        
        return EmployeeResponseDTO.from_orm(employee)
    
    async def get_employees(
        self, 
        query: EmployeeQueryDTO, 
        tenant_id: str
    ) -> EmployeeListResponseDTO:
        """获取员工列表"""
        # 构建查询条件
        conditions = [EmployeeModel.tenant_id == tenant_id, EmployeeModel.is_deleted == False]
        
        if query.name:
            conditions.append(EmployeeModel.name.ilike(f"%{query.name}%"))
        if query.employee_id:
            conditions.append(EmployeeModel.employee_id.ilike(f"%{query.employee_id}%"))
        if query.email:
            conditions.append(EmployeeModel.email.ilike(f"%{query.email}%"))
        if query.department_id:
            conditions.append(EmployeeModel.department_id == query.department_id)
        if query.position:
            conditions.append(EmployeeModel.position.ilike(f"%{query.position}%"))
        if query.manager_id:
            conditions.append(EmployeeModel.manager_id == query.manager_id)
        if query.status:
            conditions.append(EmployeeModel.status == query.status)
        
        # 查询总数
        count_stmt = select(func.count(EmployeeModel.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (query.page - 1) * query.page_size
        stmt = (
            select(EmployeeModel)
            .where(and_(*conditions))
            .options(
                selectinload(EmployeeModel.department),
                selectinload(EmployeeModel.manager)
            )
            .offset(offset)
            .limit(query.page_size)
            .order_by(EmployeeModel.created_at.desc())
        )
        
        result = await self.db.execute(stmt)
        employees = result.scalars().all()
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size
        
        return EmployeeListResponseDTO(
            items=[EmployeeResponseDTO.from_orm(employee) for employee in employees],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    async def get_employee_by_id(
        self, 
        employee_id: int, 
        tenant_id: str
    ) -> Optional[EmployeeResponseDTO]:
        """根据ID获取员工"""
        # 先尝试从缓存获取
        cached_employee = await self._get_cached_employee(employee_id, tenant_id)
        if cached_employee:
            return cached_employee
        
        # 从数据库查询
        employee = await self._get_employee_by_id_internal(employee_id, tenant_id)
        
        if employee:
            # 缓存员工信息
            await self._cache_employee(employee)
            return EmployeeResponseDTO.from_orm(employee)
        
        return None
    
    async def update_employee(
        self, 
        employee_id: int, 
        employee_data: EmployeeUpdateDTO, 
        updated_by: str, 
        tenant_id: str
    ) -> Optional[EmployeeResponseDTO]:
        """更新员工信息"""
        # 获取员工
        employee = await self._get_employee_by_id_internal(employee_id, tenant_id)
        
        if not employee:
            return None
        
        # 如果更新工号，检查是否重复
        if employee_data.employee_id and employee_data.employee_id != employee.employee_id:
            existing_employee = await self._get_employee_by_employee_id(employee_data.employee_id, tenant_id)
            if existing_employee and existing_employee.id != employee_id:
                raise ValueError(f"员工工号 {employee_data.employee_id} 已存在")
        
        # 如果更新邮箱，检查是否重复
        if employee_data.email and employee_data.email != employee.email:
            existing_email = await self._get_employee_by_email(employee_data.email, tenant_id)
            if existing_email and existing_email.id != employee_id:
                raise ValueError(f"邮箱 {employee_data.email} 已存在")
        
        # 验证部门是否存在
        if employee_data.department_id and employee_data.department_id != employee.department_id:
            department = await self._get_department_by_id(employee_data.department_id, tenant_id)
            if not department:
                raise ValueError(f"部门 {employee_data.department_id} 不存在")
        
        # 验证上级是否存在
        if employee_data.manager_id is not None and employee_data.manager_id != employee.manager_id:
            if employee_data.manager_id == employee_id:
                raise ValueError("员工不能设置自己为上级")
            
            if employee_data.manager_id > 0:
                manager = await self._get_employee_by_id_internal(employee_data.manager_id, tenant_id)
                if not manager:
                    raise ValueError(f"上级员工 {employee_data.manager_id} 不存在")
        
        # 更新字段
        update_data = employee_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        employee.updated_by = updated_by
        employee.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(employee)
        
        # 更新缓存
        await self._cache_employee(employee)
        
        return EmployeeResponseDTO.from_orm(employee)
    
    async def delete_employee(
        self, 
        employee_id: int, 
        deleted_by: str, 
        tenant_id: str
    ) -> bool:
        """删除员工（软删除）"""
        # 获取员工
        employee = await self._get_employee_by_id_internal(employee_id, tenant_id)
        
        if not employee:
            return False
        
        # 检查是否有下属员工
        subordinates = await self._get_subordinates(employee_id, tenant_id)
        if subordinates:
            raise ValueError("该员工还有下属，无法删除")
        
        # 软删除
        employee.is_deleted = True
        employee.deleted_by = deleted_by
        employee.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        
        # 清除缓存
        await self._clear_employee_cache(employee_id, tenant_id)
        
        return True
    
    async def _get_employee_by_id_internal(
        self, 
        employee_id: int, 
        tenant_id: str
    ) -> Optional[EmployeeModel]:
        """内部方法：根据ID获取员工"""
        stmt = (
            select(EmployeeModel)
            .where(
                and_(
                    EmployeeModel.id == employee_id,
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
            .options(
                selectinload(EmployeeModel.department),
                selectinload(EmployeeModel.manager)
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_employee_by_employee_id(
        self, 
        employee_id: str, 
        tenant_id: str
    ) -> Optional[EmployeeModel]:
        """根据工号获取员工"""
        stmt = (
            select(EmployeeModel)
            .where(
                and_(
                    EmployeeModel.employee_id == employee_id,
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_employee_by_email(
        self, 
        email: str, 
        tenant_id: str
    ) -> Optional[EmployeeModel]:
        """根据邮箱获取员工"""
        stmt = (
            select(EmployeeModel)
            .where(
                and_(
                    EmployeeModel.email == email,
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_department_by_id(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> Optional[DepartmentModel]:
        """根据ID获取部门"""
        stmt = (
            select(DepartmentModel)
            .where(
                and_(
                    DepartmentModel.id == department_id,
                    DepartmentModel.tenant_id == tenant_id,
                    DepartmentModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_subordinates(
        self, 
        employee_id: int, 
        tenant_id: str
    ) -> List[EmployeeModel]:
        """获取下属员工列表"""
        stmt = (
            select(EmployeeModel)
            .where(
                and_(
                    EmployeeModel.manager_id == employee_id,
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _cache_employee(self, employee: EmployeeModel) -> None:
        """缓存员工信息"""
        try:
            redis = await get_redis()
            cache_key = f"employee:{employee.tenant_id}:{employee.id}"
            employee_dto = EmployeeResponseDTO.from_orm(employee)
            serialized_data = serialize_for_cache(employee_dto)
            await redis.set(cache_key, serialized_data, expire=3600, serialize=False)  # 缓存1小时
        except Exception as e:
            # 缓存失败不影响主流程
            print(f"缓存员工信息失败: {e}")
    
    async def _get_cached_employee(
        self, 
        employee_id: int, 
        tenant_id: str
    ) -> Optional[EmployeeResponseDTO]:
        """从缓存获取员工信息"""
        try:
            redis = await get_redis()
            cache_key = f"employee:{tenant_id}:{employee_id}"
            cached_data = await redis.get(cache_key, deserialize=False)
            if cached_data:
                return deserialize_from_cache(cached_data, EmployeeResponseDTO)
        except Exception as e:
            # 缓存读取失败不影响主流程
            print(f"读取员工缓存失败: {e}")
        
        return None
    
    async def _clear_employee_cache(self, employee_id: int, tenant_id: str) -> None:
        """清除员工缓存"""
        try:
            redis = await get_redis()
            cache_key = f"employee:{tenant_id}:{employee_id}"
            await redis.delete(cache_key)
        except Exception as e:
            # 缓存清除失败不影响主流程
            print(f"清除员工缓存失败: {e}") 