"""
前台签到系统 Schema 定义
包含前台签到、主机通知、会议室管理等相关数据传输对象
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.api.models.base_response import BaseResponseModel


# 枚举定义
class CheckinMethod(str, Enum):
    """签到方法枚举"""
    QR_CODE = "qr_code"
    MANUAL = "manual"
    FACE_RECOGNITION = "face_recognition"
    ID_CARD = "id_card"
    SELF_SERVICE = "self_service"


class CheckinStatus(str, Enum):
    """签到状态枚举"""
    PENDING = "pending"
    CHECKED_IN = "checked_in"
    WAITING = "waiting"
    MEETING = "meeting"
    COMPLETED = "completed"


class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    WECHAT = "wechat"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    INTERNAL = "internal"


class NotificationStatus(str, Enum):
    """通知状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


# 前台签到相关 Schema
class ReceptionCheckinRequestSchema(BaseModel):
    """前台签到请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    reception_desk_id: str = Field(..., description="前台接待台ID")
    checkin_method: CheckinMethod = Field(..., description="签到方法")
    waiting_area_id: Optional[str] = Field(None, description="等候区域ID")
    special_requirements: Optional[List[str]] = Field(None, description="特殊需求")
    services_provided: Optional[List[str]] = Field(None, description="提供的服务")
    receptionist_id: Optional[int] = Field(None, description="接待员ID")
    checkin_notes: Optional[str] = Field(None, description="签到备注")


class ReceptionCheckinResponseSchema(BaseResponseModel):
    """前台签到响应Schema"""
    checkin_id: str = Field(..., description="签到记录ID")
    visitor_id: int = Field(..., description="访客ID")
    checkin_time: datetime = Field(..., description="签到时间")
    checkin_status: CheckinStatus = Field(..., description="签到状态")
    waiting_number: Optional[str] = Field(None, description="等候号码")
    estimated_wait_time: Optional[int] = Field(None, description="预估等待时间(分钟)")
    assigned_area: Optional[str] = Field(None, description="分配区域")
    next_steps: List[str] = Field(default=[], description="后续步骤")
    qr_code_url: Optional[str] = Field(None, description="等候二维码URL")


# 主机通知相关 Schema
class HostNotificationRequestSchema(BaseModel):
    """主机通知请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    employee_id: int = Field(..., description="员工ID")
    notification_channels: List[NotificationChannel] = Field(..., description="通知渠道")
    notification_content: Dict[str, Any] = Field(..., description="通知内容")
    priority: int = Field(1, description="优先级", ge=1, le=5)
    scheduled_time: Optional[datetime] = Field(None, description="计划发送时间")
    auto_retry: bool = Field(True, description="是否自动重试")
    max_retries: int = Field(3, description="最大重试次数", ge=0, le=10)

    @validator('notification_content')
    def validate_notification_content(cls, v):
        """验证通知内容"""
        required_fields = ['title', 'message']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"通知内容必须包含{field}字段")
        return v


class HostNotificationResponseSchema(BaseResponseModel):
    """主机通知响应Schema"""
    notification_id: str = Field(..., description="通知ID")
    visitor_id: int = Field(..., description="访客ID")
    employee_id: int = Field(..., description="员工ID")
    sent_channels: List[str] = Field(..., description="已发送渠道")
    failed_channels: List[str] = Field(default=[], description="失败渠道")
    delivery_status: Dict[str, str] = Field(..., description="投递状态")
    sent_time: datetime = Field(..., description="发送时间")
    expected_response_time: Optional[datetime] = Field(None, description="预期响应时间")


# 等候区域管理 Schema
class WaitingAreaStatusRequestSchema(BaseModel):
    """等候区域状态请求Schema"""
    area_id: Optional[str] = Field(None, description="区域ID")
    include_capacity: bool = Field(True, description="是否包含容量信息")


class WaitingAreaInfoSchema(BaseModel):
    """等候区域信息Schema"""
    area_id: str = Field(..., description="区域ID")
    area_name: str = Field(..., description="区域名称")
    capacity: int = Field(..., description="容量")
    current_visitors: int = Field(..., description="当前访客数")
    available_seats: int = Field(..., description="可用座位数")
    average_wait_time: int = Field(..., description="平均等待时间(分钟)")
    amenities: List[str] = Field(default=[], description="设施")
    status: str = Field(..., description="区域状态")


class WaitingAreaStatusResponseSchema(BaseResponseModel):
    """等候区域状态响应Schema"""
    areas: List[WaitingAreaInfoSchema] = Field(..., description="区域列表")
    total_waiting: int = Field(..., description="总等候人数")
    peak_wait_time: int = Field(..., description="峰值等待时间(分钟)")
    last_updated: datetime = Field(..., description="最后更新时间")


# 前台工作台 Schema
class ReceptionDashboardRequestSchema(BaseModel):
    """前台工作台请求Schema"""
    desk_id: str = Field(..., description="接待台ID")
    include_history: bool = Field(False, description="是否包含历史数据")


class ReceptionDashboardResponseSchema(BaseResponseModel):
    """前台工作台响应Schema"""
    desk_id: str = Field(..., description="接待台ID")
    current_queue: List[Dict[str, Any]] = Field(..., description="当前队列")
    waiting_visitors: int = Field(..., description="等候访客数")
    today_checkins: int = Field(..., description="今日签到数")
    average_service_time: int = Field(..., description="平均服务时间(分钟)")
    pending_notifications: int = Field(..., description="待处理通知数")
    active_meetings: int = Field(..., description="进行中会议数")
    system_alerts: List[str] = Field(default=[], description="系统警告")
    performance_metrics: Dict[str, Any] = Field(..., description="性能指标")


# 会议室管理 Schema
class MeetingRoomCreateRequestSchema(BaseModel):
    """会议室创建请求Schema"""
    room_name: str = Field(..., description="会议室名称")
    room_code: str = Field(..., description="会议室编码")
    capacity: int = Field(..., description="容量", ge=1)
    location: str = Field(..., description="位置")
    amenities: List[str] = Field(default=[], description="设施")
    booking_rules: Dict[str, Any] = Field(..., description="预订规则")
    hourly_rate: Optional[float] = Field(None, description="小时费率")
    is_active: bool = Field(True, description="是否启用")


class MeetingRoomResponseSchema(BaseResponseModel):
    """会议室响应Schema"""
    room_id: int = Field(..., description="会议室ID")
    room_name: str = Field(..., description="会议室名称")
    room_code: str = Field(..., description="会议室编码")
    capacity: int = Field(..., description="容量")
    location: str = Field(..., description="位置")
    amenities: List[str] = Field(..., description="设施")
    current_status: str = Field(..., description="当前状态")
    next_available: Optional[datetime] = Field(None, description="下次可用时间")
    booking_url: Optional[str] = Field(None, description="预订链接")


class MeetingRoomBookingRequestSchema(BaseModel):
    """会议室预订请求Schema"""
    room_id: int = Field(..., description="会议室ID")
    visitor_id: int = Field(..., description="访客ID")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    meeting_title: str = Field(..., description="会议主题")
    attendee_count: int = Field(..., description="参会人数", ge=1)
    special_requirements: Optional[List[str]] = Field(None, description="特殊需求")
    contact_person: Optional[str] = Field(None, description="联系人")
    booking_notes: Optional[str] = Field(None, description="预订备注")

    @validator('end_time')
    def validate_end_time(cls, v, values):
        """验证结束时间"""
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError("结束时间必须晚于开始时间")
        return v


class MeetingRoomBookingResponseSchema(BaseResponseModel):
    """会议室预订响应Schema"""
    booking_id: int = Field(..., description="预订ID")
    room_id: int = Field(..., description="会议室ID")
    visitor_id: int = Field(..., description="访客ID")
    booking_code: str = Field(..., description="预订编码")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    booking_status: str = Field(..., description="预订状态")
    access_code: Optional[str] = Field(None, description="门禁密码")
    checkin_instructions: List[str] = Field(default=[], description="签到说明")


# 访客满意度调查 Schema
class VisitorFeedbackRequestSchema(BaseModel):
    """访客满意度调查请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    service_rating: int = Field(..., description="服务评分", ge=1, le=5)
    facility_rating: int = Field(..., description="设施评分", ge=1, le=5)
    process_rating: int = Field(..., description="流程评分", ge=1, le=5)
    overall_rating: int = Field(..., description="总体评分", ge=1, le=5)
    positive_aspects: Optional[List[str]] = Field(None, description="满意方面")
    improvement_suggestions: Optional[List[str]] = Field(None, description="改进建议")
    detailed_feedback: Optional[str] = Field(None, description="详细反馈")
    would_recommend: bool = Field(True, description="是否愿意推荐")
    contact_for_followup: bool = Field(False, description="是否同意后续联系")


class VisitorFeedbackResponseSchema(BaseResponseModel):
    """访客满意度调查响应Schema"""
    feedback_id: str = Field(..., description="反馈ID")
    visitor_id: int = Field(..., description="访客ID")
    submission_time: datetime = Field(..., description="提交时间")
    overall_rating: int = Field(..., description="总体评分")
    feedback_status: str = Field(..., description="反馈状态")
    followup_required: bool = Field(..., description="是否需要跟进")
    thank_you_message: str = Field(..., description="感谢信息")


# 访客状态更新 Schema
class VisitorStatusUpdateRequestSchema(BaseModel):
    """访客状态更新请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    new_status: CheckinStatus = Field(..., description="新状态")
    location: Optional[str] = Field(None, description="当前位置")
    notes: Optional[str] = Field(None, description="状态备注")
    updated_by: str = Field(..., description="更新人")


class VisitorStatusUpdateResponseSchema(BaseResponseModel):
    """访客状态更新响应Schema"""
    visitor_id: int = Field(..., description="访客ID")
    previous_status: str = Field(..., description="之前状态")
    current_status: str = Field(..., description="当前状态")
    updated_time: datetime = Field(..., description="更新时间")
    status_duration: int = Field(..., description="状态持续时间(分钟)")
    next_actions: List[str] = Field(default=[], description="下一步操作")


# 接待员工作负载 Schema
class ReceptionistWorkloadRequestSchema(BaseModel):
    """接待员工作负载请求Schema"""
    receptionist_id: Optional[int] = Field(None, description="接待员ID")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="日期范围")


class ReceptionistWorkloadResponseSchema(BaseResponseModel):
    """接待员工作负载响应Schema"""
    receptionist_id: int = Field(..., description="接待员ID")
    receptionist_name: str = Field(..., description="接待员姓名")
    today_checkins: int = Field(..., description="今日签到数")
    average_service_time: float = Field(..., description="平均服务时间(分钟)")
    visitor_satisfaction: float = Field(..., description="访客满意度")
    pending_tasks: int = Field(..., description="待处理任务数")
    workload_status: str = Field(..., description="工作负载状态")
    performance_score: float = Field(..., description="绩效评分")


# 批量操作 Schema
class BatchCheckinRequestSchema(BaseModel):
    """批量签到请求Schema"""
    visitor_ids: List[int] = Field(..., description="访客ID列表")
    reception_desk_id: str = Field(..., description="前台接待台ID")
    batch_notes: Optional[str] = Field(None, description="批量备注")


class BatchCheckinResponseSchema(BaseResponseModel):
    """批量签到响应Schema"""
    batch_id: str = Field(..., description="批量操作ID")
    total_visitors: int = Field(..., description="总访客数")
    successful_checkins: int = Field(..., description="成功签到数")
    failed_checkins: int = Field(..., description="失败签到数")
    checkin_results: List[Dict[str, Any]] = Field(..., description="签到结果")
    batch_time: datetime = Field(..., description="批量操作时间") 