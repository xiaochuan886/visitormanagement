"""
员工数据传输对象
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.domain.base_enums import EmployeeStatus, Gender


class EmployeeCreateDTO(BaseModel):
    """员工创建DTO"""
    name: str = Field(..., description="员工姓名", min_length=1, max_length=100)
    employee_id: str = Field(..., description="员工工号", min_length=1, max_length=50)
    email: EmailStr = Field(..., description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码", max_length=20)
    department_id: int = Field(..., description="部门ID")
    position: Optional[str] = Field(None, description="职位", max_length=100)
    manager_id: Optional[int] = Field(None, description="直属上级ID")
    hire_date: Optional[date] = Field(None, description="入职日期")
    birth_date: Optional[date] = Field(None, description="出生日期")
    gender: Optional[Gender] = Field(None, description="性别")
    address: Optional[str] = Field(None, description="地址", max_length=200)
    emergency_contact: Optional[str] = Field(None, description="紧急联系人", max_length=100)
    emergency_phone: Optional[str] = Field(None, description="紧急联系电话", max_length=20)
    salary: Optional[float] = Field(None, description="薪资", ge=0)
    status: Optional[EmployeeStatus] = Field(EmployeeStatus.ACTIVE, description="员工状态")


class EmployeeUpdateDTO(BaseModel):
    """员工更新DTO"""
    name: Optional[str] = Field(None, description="员工姓名", min_length=1, max_length=100)
    employee_id: Optional[str] = Field(None, description="员工工号", min_length=1, max_length=50)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码", max_length=20)
    department_id: Optional[int] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, description="职位", max_length=100)
    manager_id: Optional[int] = Field(None, description="直属上级ID")
    hire_date: Optional[date] = Field(None, description="入职日期")
    birth_date: Optional[date] = Field(None, description="出生日期")
    gender: Optional[Gender] = Field(None, description="性别")
    address: Optional[str] = Field(None, description="地址", max_length=200)
    emergency_contact: Optional[str] = Field(None, description="紧急联系人", max_length=100)
    emergency_phone: Optional[str] = Field(None, description="紧急联系电话", max_length=20)
    salary: Optional[float] = Field(None, description="薪资", ge=0)
    status: Optional[EmployeeStatus] = Field(None, description="员工状态")


class EmployeeResponseDTO(BaseModel):
    """员工响应DTO"""
    id: int
    name: str
    employee_id: str
    email: str
    phone_number: Optional[str]
    department_id: int
    position: Optional[str]
    manager_id: Optional[int]
    hire_date: Optional[datetime]
    birth_date: Optional[datetime]
    gender: Optional[str]
    address: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    salary: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    
    class Config:
        from_attributes = True


class EmployeeListResponseDTO(BaseModel):
    """员工列表响应DTO"""
    items: List[EmployeeResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmployeeQueryDTO(BaseModel):
    """员工查询DTO"""
    name: Optional[str] = Field(None, description="员工姓名")
    employee_id: Optional[str] = Field(None, description="员工工号")
    email: Optional[str] = Field(None, description="邮箱地址")
    department_id: Optional[int] = Field(None, description="部门ID")
    position: Optional[str] = Field(None, description="职位")
    manager_id: Optional[int] = Field(None, description="直属上级ID")
    status: Optional[EmployeeStatus] = Field(None, description="员工状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小") 