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


# ===== 配置引擎仓储接口 =====

class IFormConfigurationRepository(IRepository[T], ABC):
    """表单配置数据访问接口"""
    
    @abstractmethod
    async def find_by_form_type(self, form_type: str, tenant_id: UUID) -> List[T]:
        """根据表单类型查找配置"""
        pass
    
    @abstractmethod
    async def find_active_by_form_type(self, form_type: str, tenant_id: UUID) -> Optional[T]:
        """查找指定类型的活跃表单配置"""
        pass
    
    @abstractmethod
    async def find_default_by_form_type(self, form_type: str, tenant_id: UUID) -> Optional[T]:
        """查找指定类型的默认表单配置"""
        pass
    
    @abstractmethod
    async def find_by_name(self, form_name: str, tenant_id: UUID) -> Optional[T]:
        """根据表单名称查找配置"""
        pass
    
    @abstractmethod
    async def get_latest_version(self, form_type: str, tenant_id: UUID) -> int:
        """获取指定表单类型的最新版本号"""
        pass


class IFormFieldConfigurationRepository(IRepository[T], ABC):
    """表单字段配置数据访问接口"""
    
    @abstractmethod
    async def find_by_form_config(self, form_config_id: UUID) -> List[T]:
        """根据表单配置ID查找字段列表"""
        pass
    
    @abstractmethod
    async def find_by_field_key(self, form_config_id: UUID, field_key: str) -> Optional[T]:
        """根据字段键名查找字段配置"""
        pass
    
    @abstractmethod
    async def delete_by_form_config(self, form_config_id: UUID) -> bool:
        """删除指定表单配置的所有字段"""
        pass


class IWorkflowConfigurationRepository(IRepository[T], ABC):
    """工作流配置数据访问接口"""
    
    @abstractmethod
    async def find_by_workflow_type(self, workflow_type: str, tenant_id: UUID) -> List[T]:
        """根据工作流类型查找配置"""
        pass
    
    @abstractmethod
    async def find_active_by_type(self, workflow_type: str, tenant_id: UUID) -> List[T]:
        """查找指定类型的活跃工作流配置"""
        pass
    
    @abstractmethod
    async def find_by_name(self, workflow_name: str, tenant_id: UUID) -> Optional[T]:
        """根据工作流名称查找配置"""
        pass
    
    @abstractmethod
    async def find_by_priority(self, priority: int, tenant_id: UUID) -> List[T]:
        """根据优先级查找工作流配置"""
        pass
    
    @abstractmethod
    async def get_latest_version(self, workflow_type: str, tenant_id: UUID) -> int:
        """获取指定工作流类型的最新版本号"""
        pass


class IWorkflowExecutionRepository(IRepository[T], ABC):
    """工作流执行数据访问接口"""
    
    @abstractmethod
    async def find_by_config(self, workflow_config_id: UUID) -> List[T]:
        """根据工作流配置ID查找执行记录"""
        pass
    
    @abstractmethod
    async def find_by_target_entity(
        self, 
        target_entity_type: str, 
        target_entity_id: str, 
        tenant_id: UUID
    ) -> List[T]:
        """根据目标实体查找执行记录"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str, tenant_id: UUID) -> List[T]:
        """根据执行状态查找记录"""
        pass
    
    @abstractmethod
    async def find_pending_executions(self, tenant_id: UUID) -> List[T]:
        """查找待执行的工作流"""
        pass
    
    @abstractmethod
    async def find_timeout_executions(self, tenant_id: UUID) -> List[T]:
        """查找超时的工作流执行"""
        pass


class ISpatialConfigurationRepository(IRepository[T], ABC):
    """空间配置数据访问接口"""
    
    @abstractmethod
    async def find_by_name(self, config_name: str, tenant_id: UUID) -> Optional[T]:
        """根据配置名称查找空间配置"""
        pass
    
    @abstractmethod
    async def find_active_configs(self, tenant_id: UUID) -> List[T]:
        """查找活跃的空间配置"""
        pass
    
    @abstractmethod
    async def get_latest_version(self, config_name: str, tenant_id: UUID) -> int:
        """获取指定配置的最新版本号"""
        pass


class ISpatialEntityRepository(IRepository[T], ABC):
    """空间实体数据访问接口"""
    
    @abstractmethod
    async def find_by_config(self, spatial_config_id: UUID) -> List[T]:
        """根据空间配置ID查找实体列表"""
        pass
    
    @abstractmethod
    async def find_by_entity_code(self, entity_code: str, tenant_id: UUID) -> Optional[T]:
        """根据实体编码查找空间实体"""
        pass
    
    @abstractmethod
    async def find_by_spatial_type(self, spatial_type: str, tenant_id: UUID) -> List[T]:
        """根据空间类型查找实体"""
        pass
    
    @abstractmethod
    async def find_by_parent(self, parent_id: UUID) -> List[T]:
        """根据父级ID查找子级实体"""
        pass
    
    @abstractmethod
    async def find_by_level(self, level: int, tenant_id: UUID) -> List[T]:
        """根据层级查找实体"""
        pass
    
    @abstractmethod
    async def find_hierarchy_tree(self, root_id: Optional[UUID], tenant_id: UUID) -> List[T]:
        """获取层级树结构"""
        pass
    
    @abstractmethod
    async def find_by_operating_status(self, status: str, tenant_id: UUID) -> List[T]:
        """根据运营状态查找实体"""
        pass


class IBusinessRuleRepository(IRepository[T], ABC):
    """业务规则数据访问接口"""
    
    @abstractmethod
    async def find_by_category(self, rule_category: str, tenant_id: UUID) -> List[T]:
        """根据规则类别查找规则"""
        pass
    
    @abstractmethod
    async def find_active_rules(self, tenant_id: UUID) -> List[T]:
        """查找活跃的业务规则"""
        pass
    
    @abstractmethod
    async def find_by_target_entity(self, target_entity_type: str, tenant_id: UUID) -> List[T]:
        """根据目标实体类型查找规则"""
        pass
    
    @abstractmethod
    async def find_by_priority(self, priority: int, tenant_id: UUID) -> List[T]:
        """根据优先级查找规则"""
        pass
    
    @abstractmethod
    async def find_by_name(self, rule_name: str, tenant_id: UUID) -> Optional[T]:
        """根据规则名称查找规则"""
        pass
    
    @abstractmethod
    async def find_effective_rules(self, effective_date: Any, tenant_id: UUID) -> List[T]:
        """查找在指定日期生效的规则"""
        pass
    
    @abstractmethod
    async def get_latest_version(self, rule_name: str, tenant_id: UUID) -> int:
        """获取指定规则的最新版本号"""
        pass


class IRuleExecutionLogRepository(IRepository[T], ABC):
    """规则执行日志数据访问接口"""
    
    @abstractmethod
    async def find_by_rule(self, rule_id: UUID) -> List[T]:
        """根据规则ID查找执行日志"""
        pass
    
    @abstractmethod
    async def find_by_target_entity(
        self, 
        target_entity_type: str, 
        target_entity_id: str, 
        tenant_id: UUID
    ) -> List[T]:
        """根据目标实体查找执行日志"""
        pass
    
    @abstractmethod
    async def find_by_execution_result(self, result: str, tenant_id: UUID) -> List[T]:
        """根据执行结果查找日志"""
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: Any, 
        end_date: Any, 
        tenant_id: UUID
    ) -> List[T]:
        """根据日期范围查找执行日志"""
        pass
    
    @abstractmethod
    async def get_execution_statistics(
        self, 
        rule_id: UUID, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取规则执行统计信息"""
        pass 