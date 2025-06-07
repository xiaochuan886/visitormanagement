"""
数据访问接口定义
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
from uuid import UUID

from app.domain.entities.base import BaseEntity

T = TypeVar('T', bound=BaseEntity)


class IRepository(Generic[T], ABC):
    """通用数据访问接口"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """创建实体"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """根据ID获取实体"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有实体"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """更新实体"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """删除实体"""
        pass
    
    @abstractmethod
    async def find_by(self, filters: Dict[str, Any]) -> List[T]:
        """根据条件查找实体"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计实体数量"""
        pass


class IVisitorRepository(IRepository[T], ABC):
    """访客数据访问接口"""
    
    @abstractmethod
    async def find_by_phone(self, phone: str, tenant_id: UUID) -> Optional[T]:
        """根据手机号查找访客"""
        pass
    
    @abstractmethod
    async def find_by_id_card(self, id_card: str, tenant_id: UUID) -> Optional[T]:
        """根据身份证号查找访客"""
        pass
    
    @abstractmethod
    async def find_active_visits(self, tenant_id: UUID) -> List[T]:
        """查找当前活跃的访问记录"""
        pass
    
    @abstractmethod
    async def find_by_employee(self, employee_id: UUID, tenant_id: UUID) -> List[T]:
        """根据被访员工查找访客"""
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: Any, 
        end_date: Any, 
        tenant_id: UUID
    ) -> List[T]:
        """根据日期范围查找访客"""
        pass


class IEmployeeRepository(IRepository[T], ABC):
    """员工数据访问接口"""
    
    @abstractmethod
    async def find_by_email(self, email: str, tenant_id: UUID) -> Optional[T]:
        """根据邮箱查找员工"""
        pass
    
    @abstractmethod
    async def find_by_employee_number(self, employee_number: str, tenant_id: UUID) -> Optional[T]:
        """根据工号查找员工"""
        pass
    
    @abstractmethod
    async def find_by_department(self, department_id: UUID, tenant_id: UUID) -> List[T]:
        """根据部门查找员工"""
        pass


class IDepartmentRepository(IRepository[T], ABC):
    """部门数据访问接口"""
    
    @abstractmethod
    async def find_by_name(self, name: str, tenant_id: UUID) -> Optional[T]:
        """根据名称查找部门"""
        pass
    
    @abstractmethod
    async def find_children(self, parent_id: UUID, tenant_id: UUID) -> List[T]:
        """查找子部门"""
        pass


class ISiteRepository(IRepository[T], ABC):
    """站点数据访问接口"""
    
    @abstractmethod
    async def find_by_code(self, code: str, tenant_id: UUID) -> Optional[T]:
        """根据编码查找站点"""
        pass
    
    @abstractmethod
    async def find_active_sites(self, tenant_id: UUID) -> List[T]:
        """查找活跃站点"""
        pass 