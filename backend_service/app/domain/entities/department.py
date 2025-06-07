"""
部门实体定义
"""
from typing import Optional
from pydantic import Field

from .base import TenantEntity


class Department(TenantEntity):
    """部门实体"""
    
    # 基本信息
    name: str = Field(..., description="部门名称")
    code: Optional[str] = Field(None, description="部门编码")
    description: Optional[str] = Field(None, description="部门描述")
    
    # 层级关系
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    sort_order: int = Field(0, description="排序顺序")
    
    # 联系信息
    phone: Optional[str] = Field(None, description="部门电话")
    email: Optional[str] = Field(None, description="部门邮箱")
    address: Optional[str] = Field(None, description="办公地址")
    
    # 负责人信息
    manager_id: Optional[int] = Field(None, description="部门经理ID")
    
    # 关联信息
    site_id: Optional[int] = Field(None, description="所属站点ID")
    
    @property
    def is_root_department(self) -> bool:
        """是否为根部门"""
        return self.parent_id is None 