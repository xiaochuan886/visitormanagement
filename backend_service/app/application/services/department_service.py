"""
部门服务层
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import DepartmentModel, EmployeeModel
from app.application.dto.department_dto import (
    DepartmentCreateDTO,
    DepartmentUpdateDTO,
    DepartmentResponseDTO,
    DepartmentListResponseDTO,
    DepartmentQueryDTO
)
from app.domain.enums import EmployeeStatus
from app.infrastructure.cache.redis_client import get_redis
from app.core.config import settings


class DepartmentService:
    """部门服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_department(
        self, 
        department_data: DepartmentCreateDTO, 
        created_by: str, 
        tenant_id: str
    ) -> DepartmentResponseDTO:
        """创建部门"""
        # 检查部门编码是否已存在
        existing_department = await self._get_department_by_code(department_data.code, tenant_id)
        if existing_department:
            raise ValueError(f"部门编码 {department_data.code} 已存在")
        
        # 验证上级部门是否存在
        if department_data.parent_id:
            parent_department = await self._get_department_by_id_internal(department_data.parent_id, tenant_id)
            if not parent_department:
                raise ValueError(f"上级部门 {department_data.parent_id} 不存在")
        
        # 创建部门模型
        department = DepartmentModel(
            name=department_data.name,
            code=department_data.code,
            description=department_data.description,
            parent_id=department_data.parent_id,
            manager_id=department_data.manager_id,
            site_id=department_data.site_id,
            phone=department_data.phone_number,  # 字段名映射
            email=department_data.email,
            address=department_data.location,  # 字段名映射
            tenant_id=tenant_id,
            created_by=created_by
        )
        
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        
        # 缓存部门信息 (暂时禁用)
        await self._cache_department(department)
        
        return DepartmentResponseDTO.from_orm(department)
    
    async def get_departments(
        self, 
        query: DepartmentQueryDTO, 
        tenant_id: str
    ) -> DepartmentListResponseDTO:
        """获取部门列表"""
        # 构建查询条件
        conditions = [DepartmentModel.tenant_id == tenant_id, DepartmentModel.is_deleted == False]
        
        if query.name:
            conditions.append(DepartmentModel.name.ilike(f"%{query.name}%"))
        if query.code:
            conditions.append(DepartmentModel.code.ilike(f"%{query.code}%"))
        if query.parent_id is not None:
            conditions.append(DepartmentModel.parent_id == query.parent_id)
        if query.manager_id:
            conditions.append(DepartmentModel.manager_id == query.manager_id)
        if query.site_id:
            conditions.append(DepartmentModel.site_id == query.site_id)
        if query.status:
            conditions.append(DepartmentModel.status == query.status)
        
        # 查询总数
        count_stmt = select(func.count(DepartmentModel.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (query.page - 1) * query.page_size
        stmt = (
            select(DepartmentModel)
            .where(and_(*conditions))
            .options(
                selectinload(DepartmentModel.parent),
                selectinload(DepartmentModel.manager),
                selectinload(DepartmentModel.site)
            )
            .offset(offset)
            .limit(query.page_size)
            .order_by(DepartmentModel.created_at.desc())
        )
        
        result = await self.db.execute(stmt)
        departments = result.scalars().all()
        
        # 计算员工数量
        for department in departments:
            employee_count = await self._get_department_employee_count(department.id, tenant_id)
            department.employee_count = employee_count
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size
        
        return DepartmentListResponseDTO(
            items=[DepartmentResponseDTO.from_orm(department) for department in departments],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    async def get_department_by_id(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> Optional[DepartmentResponseDTO]:
        """根据ID获取部门"""
        # 先尝试从缓存获取 (暂时禁用)
        cached_department = await self._get_cached_department(department_id, tenant_id)
        if cached_department:
            return cached_department
        
        # 从数据库查询
        department = await self._get_department_by_id_internal(department_id, tenant_id)
        
        if department:
            # 获取员工数量
            employee_count = await self._get_department_employee_count(department_id, tenant_id)
            department.employee_count = employee_count
            
            # 缓存部门信息 (暂时禁用)
            await self._cache_department(department)
            return DepartmentResponseDTO.from_orm(department)
        
        return None
    
    async def update_department(
        self, 
        department_id: int, 
        department_data: DepartmentUpdateDTO, 
        updated_by: str, 
        tenant_id: str
    ) -> Optional[DepartmentResponseDTO]:
        """更新部门信息"""
        # 获取部门
        department = await self._get_department_by_id_internal(department_id, tenant_id)
        
        if not department:
            return None
        
        # 如果更新编码，检查是否重复
        if department_data.code and department_data.code != department.code:
            existing_department = await self._get_department_by_code(department_data.code, tenant_id)
            if existing_department and existing_department.id != department_id:
                raise ValueError(f"部门编码 {department_data.code} 已存在")
        
        # 验证上级部门是否存在（如果有更新）
        if department_data.parent_id is not None and department_data.parent_id != department.parent_id:
            if department_data.parent_id == department_id:
                raise ValueError("部门不能设置自己为上级部门")
            
            if department_data.parent_id > 0:
                parent_department = await self._get_department_by_id_internal(department_data.parent_id, tenant_id)
                if not parent_department:
                    raise ValueError(f"上级部门 {department_data.parent_id} 不存在")
                
                # 检查是否会形成循环引用
                if await self._would_create_cycle(department_id, department_data.parent_id, tenant_id):
                    raise ValueError("设置上级部门会形成循环引用")
        
        # 更新字段
        update_data = department_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        department.updated_by = updated_by
        department.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(department)
        
        # 更新缓存 (暂时禁用)
        await self._cache_department(department)
        
        return DepartmentResponseDTO.from_orm(department)
    
    async def delete_department(
        self, 
        department_id: int, 
        deleted_by: str, 
        tenant_id: str
    ) -> bool:
        """删除部门（软删除）"""
        # 获取部门
        department = await self._get_department_by_id_internal(department_id, tenant_id)
        
        if not department:
            return False
        
        # 检查是否有子部门
        child_departments = await self._get_child_departments(department_id, tenant_id)
        if child_departments:
            raise ValueError("存在子部门，无法删除")
        
        # 检查是否有员工
        employee_count = await self._get_department_employee_count(department_id, tenant_id)
        if employee_count > 0:
            raise ValueError("部门下还有员工，无法删除")
        
        # 软删除
        department.is_deleted = True
        department.deleted_by = deleted_by
        department.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        
        # 清除缓存 (暂时禁用)
        await self._clear_department_cache(department_id, tenant_id)
        
        return True
    
    async def _get_department_by_id_internal(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> Optional[DepartmentModel]:
        """内部方法：根据ID获取部门"""
        stmt = (
            select(DepartmentModel)
            .where(
                and_(
                    DepartmentModel.id == department_id,
                    DepartmentModel.tenant_id == tenant_id,
                    DepartmentModel.is_deleted == False
                )
            )
            .options(
                selectinload(DepartmentModel.parent),
                selectinload(DepartmentModel.manager),
                selectinload(DepartmentModel.site)
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_department_by_code(
        self, 
        code: str, 
        tenant_id: str
    ) -> Optional[DepartmentModel]:
        """根据编码获取部门"""
        stmt = (
            select(DepartmentModel)
            .where(
                and_(
                    DepartmentModel.code == code,
                    DepartmentModel.tenant_id == tenant_id,
                    DepartmentModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_child_departments(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> List[DepartmentModel]:
        """获取子部门列表"""
        stmt = (
            select(DepartmentModel)
            .where(
                and_(
                    DepartmentModel.parent_id == department_id,
                    DepartmentModel.tenant_id == tenant_id,
                    DepartmentModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _get_department_employee_count(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> int:
        """获取部门员工数量"""
        stmt = (
            select(func.count(EmployeeModel.id))
            .where(
                and_(
                    EmployeeModel.department_id == department_id,
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def _would_create_cycle(
        self, 
        department_id: int, 
        parent_id: int, 
        tenant_id: str
    ) -> bool:
        """检查是否会形成循环引用"""
        current_id = parent_id
        visited = set()
        
        while current_id and current_id not in visited:
            if current_id == department_id:
                return True
            
            visited.add(current_id)
            
            # 获取当前部门的上级部门
            stmt = (
                select(DepartmentModel.parent_id)
                .where(
                    and_(
                        DepartmentModel.id == current_id,
                        DepartmentModel.tenant_id == tenant_id,
                        DepartmentModel.is_deleted == False
                    )
                )
            )
            
            result = await self.db.execute(stmt)
            current_id = result.scalar()
        
        return False
    
    async def _cache_department(self, department: DepartmentModel) -> None:
        """缓存部门信息"""
        try:
            redis = await get_redis()
            cache_key = f"department:{department.tenant_id}:{department.id}"
            department_data = DepartmentResponseDTO.from_orm(department).dict()
            await redis.setex(cache_key, 3600, str(department_data))  # 缓存1小时
        except Exception as e:
            # 缓存失败不影响主流程
            print(f"缓存部门信息失败: {e}")
    
    async def _get_cached_department(
        self, 
        department_id: int, 
        tenant_id: str
    ) -> Optional[DepartmentResponseDTO]:
        """从缓存获取部门信息"""
        try:
            redis = await get_redis()
            cache_key = f"department:{tenant_id}:{department_id}"
            cached_data = await redis.get(cache_key)
            if cached_data:
                department_dict = eval(cached_data)  # 注意：生产环境应使用json.loads
                return DepartmentResponseDTO(**department_dict)
        except Exception as e:
            # 缓存读取失败不影响主流程
            print(f"读取部门缓存失败: {e}")
        
        return None
    
    async def _clear_department_cache(self, department_id: int, tenant_id: str) -> None:
        """清除部门缓存"""
        try:
            redis = await get_redis()
            cache_key = f"department:{tenant_id}:{department_id}"
            await redis.delete(cache_key)
        except Exception as e:
            # 缓存清除失败不影响主流程
            print(f"清除部门缓存失败: {e}") 