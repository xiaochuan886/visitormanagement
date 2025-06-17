"""
访客实体定义
"""
from datetime import datetime, time
from typing import Optional, List
from pydantic import Field, EmailStr

from .base import TenantEntity, DomainEvent
from ..base_enums import VisitorStatus, Gender, ApprovalOutcome, VisitPurpose


class Visitor(TenantEntity):
    """访客实体"""
    
    # 基本信息
    pass_code: Optional[str] = Field(None, description="通行码")
    name: str = Field(..., description="访客姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone_number: Optional[str] = Field(None, description="电话号码")
    identification_no: Optional[str] = Field(None, description="证件号码")
    license_plate_number: Optional[str] = Field(None, description="车牌号")
    address: Optional[str] = Field(None, description="地址")
    gender: Optional[Gender] = Field(None, description="性别")
    company_name: Optional[str] = Field(None, description="公司名称")
    
    # 访问信息
    purpose: Optional[VisitPurpose] = Field(None, description="访问目的")
    comment: Optional[str] = Field(None, description="备注")
    designation_id: Optional[int] = Field(None, description="职位ID")
    employee_id: Optional[int] = Field(None, description="被访问员工ID")
    
    # 时间信息
    checkin_date: Optional[datetime] = Field(None, description="签到时间")
    checkout_date: Optional[datetime] = Field(None, description="签出时间")
    expected_date: Optional[datetime] = Field(None, description="预期访问日期")
    expected_time: Optional[time] = Field(None, description="预期访问时间")
    
    # 附加信息
    avatar: Optional[str] = Field(None, description="头像URL")
    trip_code: Optional[str] = Field(None, description="行程码")
    health_code: Optional[str] = Field(None, description="健康码")
    qr_code: Optional[str] = Field(None, description="二维码")
    nucleic_acid_test_report: Optional[str] = Field(None, description="核酸检测报告")
    
    # 协议和承诺
    privacy_policy: Optional[bool] = Field(None, description="是否同意隐私政策")
    promise: Optional[bool] = Field(None, description="是否承诺信息真实")
    
    # 状态信息
    status: VisitorStatus = Field(VisitorStatus.PENDING, description="访客状态")
    approved: Optional[bool] = Field(None, description="是否已审批")
    approval_outcome: Optional[ApprovalOutcome] = Field(None, description="审批结果")
    approval_comment: Optional[str] = Field(None, description="审批意见")
    
    # 关联信息
    site_id: Optional[int] = Field(None, description="站点ID")
    survey_response_value: Optional[int] = Field(None, description="调查问卷得分")
    
    # 领域事件
    domain_events: List[DomainEvent] = Field(default_factory=list, description="领域事件")
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        self.domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """清除并返回领域事件"""
        events = self.domain_events.copy()
        self.domain_events.clear()
        return events
    
    def approve(self, approver: str, comment: Optional[str] = None) -> None:
        """审批通过"""
        self.approved = True
        self.approval_outcome = ApprovalOutcome.APPROVED
        self.approval_comment = comment
        self.status = VisitorStatus.APPROVED
        self.updated_by = approver
        self.updated_at = datetime.utcnow()
        
        # 添加审批事件
        self.add_domain_event(DomainEvent(
            event_type="visitor_approved",
            aggregate_id=str(self.id),
            aggregate_type="Visitor",
            event_data={
                "visitor_id": self.id,
                "approver": approver,
                "comment": comment
            }
        ))
    
    def reject(self, approver: str, comment: Optional[str] = None) -> None:
        """审批拒绝"""
        self.approved = False
        self.approval_outcome = ApprovalOutcome.REJECTED
        self.approval_comment = comment
        self.status = VisitorStatus.REJECTED
        self.updated_by = approver
        self.updated_at = datetime.utcnow()
        
        # 添加拒绝事件
        self.add_domain_event(DomainEvent(
            event_type="visitor_rejected",
            aggregate_id=str(self.id),
            aggregate_type="Visitor",
            event_data={
                "visitor_id": self.id,
                "approver": approver,
                "comment": comment
            }
        ))
    
    def checkin(self, checkin_point_id: Optional[int] = None) -> None:
        """签到"""
        self.checkin_date = datetime.utcnow()
        self.status = VisitorStatus.CHECKED_IN
        self.updated_at = datetime.utcnow()
        
        # 添加签到事件
        self.add_domain_event(DomainEvent(
            event_type="visitor_checked_in",
            aggregate_id=str(self.id),
            aggregate_type="Visitor",
            event_data={
                "visitor_id": self.id,
                "checkin_time": self.checkin_date.isoformat(),
                "checkin_point_id": checkin_point_id
            }
        ))
    
    def checkout(self, checkout_point_id: Optional[int] = None) -> None:
        """签出"""
        self.checkout_date = datetime.utcnow()
        self.status = VisitorStatus.CHECKED_OUT
        self.updated_at = datetime.utcnow()
        
        # 添加签出事件
        self.add_domain_event(DomainEvent(
            event_type="visitor_checked_out",
            aggregate_id=str(self.id),
            aggregate_type="Visitor",
            event_data={
                "visitor_id": self.id,
                "checkout_time": self.checkout_date.isoformat(),
                "checkout_point_id": checkout_point_id
            }
        ))
    
    @property
    def is_checked_in(self) -> bool:
        """是否已签到"""
        return self.status == VisitorStatus.CHECKED_IN
    
    @property
    def is_checked_out(self) -> bool:
        """是否已签出"""
        return self.status == VisitorStatus.CHECKED_OUT
    
    @property
    def visit_duration(self) -> Optional[int]:
        """访问时长（分钟）"""
        if self.checkin_date and self.checkout_date:
            return int((self.checkout_date - self.checkin_date).total_seconds() / 60)
        return None 