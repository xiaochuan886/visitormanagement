"""
站点数据传输对象
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.domain.base_enums import SiteStatus


class SiteCreateDTO(BaseModel):
    """站点创建DTO"""
    name: str = Field(..., description="站点名称", min_length=1, max_length=100)
    code: str = Field(..., description="站点编码", min_length=1, max_length=50)
    address: str = Field(..., description="站点地址", min_length=1, max_length=200)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    postal_code: Optional[str] = Field(None, description="邮政编码", max_length=20)
    phone_number: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    description: Optional[str] = Field(None, description="站点描述", max_length=500)
    working_hours_start: Optional[time] = Field(None, description="工作开始时间")
    working_hours_end: Optional[time] = Field(None, description="工作结束时间")
    timezone: Optional[str] = Field(None, description="时区", max_length=50)
    capacity: Optional[int] = Field(None, description="容量", ge=0)
    status: Optional[SiteStatus] = Field(SiteStatus.ACTIVE, description="站点状态")


class SiteUpdateDTO(BaseModel):
    """站点更新DTO"""
    name: Optional[str] = Field(None, description="站点名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="站点编码", min_length=1, max_length=50)
    address: Optional[str] = Field(None, description="站点地址", min_length=1, max_length=200)
    city: Optional[str] = Field(None, description="城市", max_length=50)
    province: Optional[str] = Field(None, description="省份", max_length=50)
    postal_code: Optional[str] = Field(None, description="邮政编码", max_length=20)
    phone_number: Optional[str] = Field(None, description="联系电话", max_length=20)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    description: Optional[str] = Field(None, description="站点描述", max_length=500)
    working_hours_start: Optional[time] = Field(None, description="工作开始时间")
    working_hours_end: Optional[time] = Field(None, description="工作结束时间")
    timezone: Optional[str] = Field(None, description="时区", max_length=50)
    capacity: Optional[int] = Field(None, description="容量", ge=0)
    status: Optional[SiteStatus] = Field(None, description="站点状态")


class SiteResponseDTO(BaseModel):
    """站点响应DTO"""
    id: int
    name: str
    code: str
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    phone: Optional[str]  # 匹配数据库字段名
    email: Optional[str]
    description: Optional[str]
    working_hours_start: Optional[str]  # 数据库中存储为字符串
    working_hours_end: Optional[str]    # 数据库中存储为字符串
    timezone: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    
    class Config:
        from_attributes = True


class SiteListResponseDTO(BaseModel):
    """站点列表响应DTO"""
    items: List[SiteResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


class SiteQueryDTO(BaseModel):
    """站点查询DTO"""
    name: Optional[str] = Field(None, description="站点名称")
    code: Optional[str] = Field(None, description="站点编码")
    city: Optional[str] = Field(None, description="城市")
    province: Optional[str] = Field(None, description="省份")
    status: Optional[SiteStatus] = Field(None, description="站点状态")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小") 