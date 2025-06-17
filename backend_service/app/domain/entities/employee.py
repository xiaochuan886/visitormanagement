"""
员工实体定义
"""
from typing import Optional
from pydantic import Field, EmailStr

from .base import TenantEntity
from ..base_enums import Gender, EmployeeStatus


class Employee(TenantEntity):
    """员工实体"""
    
    # 基本信息
    name: str = Field(..., description="员工姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码")
    gender: Optional[Gender] = Field(None, description="性别")
    
    # 组织信息
    department_id: Optional[int] = Field(None, description="部门ID")
    designation_id: Optional[int] = Field(None, description="职位ID")
    
    # 职业信息
    about: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")
    employee_number: Optional[str] = Field(None, description="工号")
    
    # 状态信息
    status: EmployeeStatus = Field(EmployeeStatus.ACTIVE, description="员工状态")
    
    # 关联信息
    related_account_id: Optional[str] = Field(None, description="关联账户ID")
    site_id: Optional[int] = Field(None, description="所属站点ID")
    
    @property
    def is_active(self) -> bool:
        """是否为在职状态"""
        return self.status == EmployeeStatus.ACTIVE
    
    def activate(self) -> None:
        """激活员工"""
        self.status = EmployeeStatus.ACTIVE
    
    def deactivate(self) -> None:
        """停用员工"""
        self.status = EmployeeStatus.INACTIVE
    
    def suspend(self) -> None:
        """暂停员工"""
        self.status = EmployeeStatus.SUSPENDED 