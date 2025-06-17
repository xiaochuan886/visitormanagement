"""
部门数据传输对象
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.domain.base_enums import EmployeeStatus


class DepartmentCreateDTO(BaseModel):
    """部门创建DTO"""
    name: str = Field(..., description="部门名称", min_length=1, max_length=100)
    code: str = Field(..., description="部门编码", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="部门描述", max_length=500)
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    manager_id: Optional[int] = Field(None, description="部门经理ID")
    site_id: Optional[int] = Field(None, description="所属站点ID")
    phone_number: Optional[str] = Field(None, description="部门电话", max_length=20)
    email: Optional[str] = Field(None, description="部门邮箱", max_length=100)
    location: Optional[str] = Field(None, description="办公地点", max_length=200)
    budget: Optional[float] = Field(None, description="部门预算", ge=0)
    status: Optional[EmployeeStatus] = Field(EmployeeStatus.ACTIVE, description="部门状态")


class DepartmentUpdateDTO(BaseModel):
    """部门更新DTO"""
    name: Optional[str] = Field(None, description="部门名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="部门编码", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="部门描述", max_length=500)
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    manager_id: Optional[int] = Field(None, description="部门经理ID")
    site_id: Optional[int] = Field(None, description="所属站点ID")
    phone_number: Optional[str] = Field(None, description="部门电话", max_length=20)
    email: Optional[str] = Field(None, description="部门邮箱", max_length=100)
    location: Optional[str] = Field(None, description="办公地点", max_length=200)
    budget: Optional[float] = Field(None, description="部门预算", ge=0)
    status: Optional[EmployeeStatus] = Field(None, description="部门状态")


class DepartmentResponseDTO(BaseModel):
    """部门响应DTO"""
    id: int
    name: str
    code: Optional[str]
    description: Optional[str]
    parent_id: Optional[int]
    manager_id: Optional[int]
    site_id: Optional[int]
    phone: Optional[str]  # 匹配数据库字段名
    email: Optional[str]
    address: Optional[str]  # 匹配数据库字段名
    sort_order: Optional[int] = Field(None, description="排序")
    employee_count: Optional[int] = Field(None, description="员工数量")
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    
    class Config:
        from_attributes = True


class DepartmentListResponseDTO(BaseModel):
    """部门列表响应DTO"""
    items: List[DepartmentResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


class DepartmentQueryDTO(BaseModel):
    """部门查询DTO"""
    name: Optional[str] = Field(None, description="部门名称")
    code: Optional[str] = Field(None, description="部门编码")
    parent_id: Optional[int] = Field(None, description="上级部门ID")
    manager_id: Optional[int] = Field(None, description="部门经理ID")
    site_id: Optional[int] = Field(None, description="所属站点ID")
    status: Optional[EmployeeStatus] = Field(None, description="部门状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小") 