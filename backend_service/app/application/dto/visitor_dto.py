"""
访客数据传输对象
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.domain.base_enums import VisitorStatus, Gender, ApprovalOutcome, VisitPurpose


class VisitorCreateDTO(BaseModel):
    """访客创建DTO"""
    name: str = Field(..., description="访客姓名", min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码", max_length=20)
    identification_no: Optional[str] = Field(None, description="证件号码", max_length=50)
    license_plate_number: Optional[str] = Field(None, description="车牌号", max_length=20)
    address: Optional[str] = Field(None, description="地址", max_length=200)
    gender: Optional[Gender] = Field(None, description="性别")
    company_name: Optional[str] = Field(None, description="公司名称", max_length=100)
    purpose: Optional[VisitPurpose] = Field(None, description="访问目的")
    comment: Optional[str] = Field(None, description="备注")
    employee_id: Optional[int] = Field(None, description="被访问员工ID")
    expected_date: Optional[datetime] = Field(None, description="预期访问日期")
    expected_time: Optional[time] = Field(None, description="预期访问时间")
    privacy_policy: Optional[bool] = Field(None, description="是否同意隐私政策")
    promise: Optional[bool] = Field(None, description="是否承诺信息真实")
    site_id: Optional[int] = Field(None, description="站点ID")


class VisitorUpdateDTO(BaseModel):
    """访客更新DTO"""
    name: Optional[str] = Field(None, description="访客姓名", min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码", max_length=20)
    identification_no: Optional[str] = Field(None, description="证件号码", max_length=50)
    license_plate_number: Optional[str] = Field(None, description="车牌号", max_length=20)
    address: Optional[str] = Field(None, description="地址", max_length=200)
    gender: Optional[Gender] = Field(None, description="性别")
    company_name: Optional[str] = Field(None, description="公司名称", max_length=100)
    purpose: Optional[VisitPurpose] = Field(None, description="访问目的")
    comment: Optional[str] = Field(None, description="备注")
    employee_id: Optional[int] = Field(None, description="被访问员工ID")
    expected_date: Optional[datetime] = Field(None, description="预期访问日期")
    expected_time: Optional[time] = Field(None, description="预期访问时间")
    site_id: Optional[int] = Field(None, description="站点ID")


class VisitorResponseDTO(BaseModel):
    """访客响应DTO"""
    id: int
    pass_code: Optional[str]
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    identification_no: Optional[str]
    license_plate_number: Optional[str]
    address: Optional[str]
    gender: Optional[str]
    company_name: Optional[str]
    purpose: Optional[str]
    comment: Optional[str]
    employee_id: Optional[int]
    checkin_date: Optional[datetime]
    checkout_date: Optional[datetime]
    expected_date: Optional[datetime]
    expected_time: Optional[time]
    avatar: Optional[str]
    status: str
    approved: Optional[bool]
    approval_outcome: Optional[str]
    approval_comment: Optional[str]
    site_id: Optional[int]
    # 门岗前台扩展字段
    current_status: Optional[str] = Field(None, description="当前状态")
    entry_time: Optional[datetime] = Field(None, description="实际入园时间")
    exit_time: Optional[datetime] = Field(None, description="实际离园时间")
    current_location: Optional[str] = Field(None, description="当前位置")
    reception_desk_id: Optional[str] = Field(None, description="签到的前台设备ID")
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    
    class Config:
        from_attributes = True


class VisitorListResponseDTO(BaseModel):
    """访客列表响应DTO"""
    items: List[VisitorResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int


class VisitorApprovalDTO(BaseModel):
    """访客审批DTO"""
    approval_outcome: ApprovalOutcome = Field(..., description="审批结果")
    approval_comment: Optional[str] = Field(None, description="审批意见", max_length=500)


class VisitorCheckinDTO(BaseModel):
    """访客签到DTO"""
    checkin_point_id: Optional[int] = Field(None, description="签到点ID")


class VisitorCheckoutDTO(BaseModel):
    """访客签出DTO"""
    checkout_point_id: Optional[int] = Field(None, description="签出点ID")


class VisitorQueryDTO(BaseModel):
    """访客查询DTO"""
    name: Optional[str] = Field(None, description="访客姓名")
    phone_number: Optional[str] = Field(None, description="电话号码")
    email: Optional[str] = Field(None, description="邮箱")
    status: Optional[VisitorStatus] = Field(None, description="访客状态")
    employee_id: Optional[int] = Field(None, description="被访问员工ID")
    site_id: Optional[int] = Field(None, description="站点ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页大小") 