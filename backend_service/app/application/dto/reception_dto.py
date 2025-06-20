"""
前台签到系统数据传输对象
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class CheckinMethod(str, Enum):
    """签到方式枚举"""
    QR_CODE = "qr_code"
    ID_CARD = "id_card"
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    PHONE_VERIFICATION = "phone_verification"


class CheckinStatus(str, Enum):
    """签到状态枚举"""
    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    HOST_UNAVAILABLE = "host_unavailable"
    ROOM_UNAVAILABLE = "room_unavailable"
    COMPLETED = "completed"
    WAITING = "waiting"


class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    SMS = "sms"
    EMAIL = "email"
    WECHAT = "wechat"
    PHONE_CALL = "phone_call"
    APP_PUSH = "app_push"


class NotificationStatus(str, Enum):
    """通知状态枚举"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    PENDING = "pending"


class EmployeeAvailability(str, Enum):
    """员工可用状态枚举"""
    AVAILABLE = "available"
    BUSY = "busy"
    IN_MEETING = "in_meeting"
    OUT_OF_OFFICE = "out_of_office"
    UNKNOWN = "unknown"


class ServiceRequestType(str, Enum):
    """服务请求类型枚举"""
    WIFI_ACCESS = "wifi_access"
    MEETING_ROOM = "meeting_room"
    PARKING = "parking"
    CATERING = "catering"
    TECHNICAL_SUPPORT = "technical_support"
    TRANSLATION = "translation"
    ESCORT = "escort"
    OTHER = "other"


class ServiceRequestStatus(str, Enum):
    """服务请求状态枚举"""
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceType(str, Enum):
    """服务类型枚举"""
    RECEPTION = "reception"
    MEETING_ARRANGEMENT = "meeting_arrangement"
    FACILITY_SERVICE = "facility_service"
    TECHNICAL_SUPPORT = "technical_support"
    VIP_SERVICE = "vip_service"


class FeedbackRating(int, Enum):
    """反馈评分枚举"""
    VERY_POOR = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5


class ReceptionCheckinDTO(BaseModel):
    """前台签到DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    checkin_id: str = Field(..., description="签到记录ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visitor_phone: str = Field(..., description="访客电话")
    
    # 签到信息
    checkin_time: datetime = Field(default_factory=datetime.now, description="签到时间")
    receptionist: str = Field(..., description="前台接待员ID")
    reception_desk: str = Field(..., description="前台位置")
    
    # 健康检查
    temperature: Optional[float] = Field(None, description="体温检测", ge=35.0, le=42.0)
    health_code_status: Optional[str] = Field(None, description="健康码状态")
    health_declaration: bool = Field(default=True, description="健康声明确认")
    
    # 安全须知
    security_briefing_completed: bool = Field(default=False, description="安全须知是否已告知")
    visitor_badge_issued: Optional[str] = Field(None, description="访客证号码")
    temporary_access_card: Optional[str] = Field(None, description="临时门禁卡号")
    
    # 等候安排
    waiting_area_assigned: Optional[str] = Field(None, description="分配的等候区")
    seat_number: Optional[str] = Field(None, description="座位号")
    estimated_wait_time: Optional[int] = Field(None, description="预估等待时间（分钟）")
    
    # 特殊需求
    special_requirements: List[str] = Field(default_factory=list, description="特殊需求")
    language_preference: Optional[str] = Field(None, description="语言偏好")
    accessibility_needs: List[str] = Field(default_factory=list, description="无障碍需求")
    
    checkin_status: CheckinStatus = Field(..., description="签到状态")
    remarks: Optional[str] = Field(None, description="备注信息")


class HostNotificationDTO(BaseModel):
    """被访人通知DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    notification_id: str = Field(..., description="通知ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visitor_company: Optional[str] = Field(None, description="访客公司")
    
    # 被访人信息
    employee_id: int = Field(..., description="被访员工ID")
    employee_name: str = Field(..., description="被访员工姓名")
    employee_phone: str = Field(..., description="被访员工电话")
    department_name: str = Field(..., description="部门名称")
    
    # 通知内容
    notification_type: str = Field(..., description="通知类型: arrival|waiting|urgent")
    message_content: str = Field(..., description="通知消息内容")
    arrival_time: datetime = Field(..., description="访客到达时间")
    
    # 等候信息
    waiting_location: str = Field(..., description="等候位置")
    estimated_wait_time: Optional[int] = Field(None, description="预估等候时间")
    
    # 通知渠道
    notification_channels: List[str] = Field(..., description="通知渠道: sms|email|wechat|call")
    
    # 状态信息
    notification_status: NotificationStatus = Field(..., description="通知状态")
    sent_time: datetime = Field(default_factory=datetime.now, description="发送时间")
    delivered_time: Optional[datetime] = Field(None, description="送达时间")
    read_time: Optional[datetime] = Field(None, description="读取时间")
    
    # 响应信息
    host_response: Optional[str] = Field(None, description="被访人回复")
    response_time: Optional[datetime] = Field(None, description="回复时间")
    estimated_arrival_time: Optional[datetime] = Field(None, description="预计到达时间")
    
    sender: str = Field(..., description="发送者ID")


class HostAvailabilityDTO(BaseModel):
    """被访人可用性DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    employee_id: int = Field(..., description="员工ID")
    employee_name: str = Field(..., description="员工姓名")
    department_name: str = Field(..., description="部门名称")
    office_location: Optional[str] = Field(None, description="办公位置")
    
    # 在岗状态
    availability_status: EmployeeAvailability = Field(..., description="可用状态")
    in_office: bool = Field(..., description="是否在办公室")
    last_checkin_time: Optional[datetime] = Field(None, description="最后签到时间")
    
    # 日程信息
    current_meeting: Optional[Dict[str, Any]] = Field(None, description="当前会议信息")
    next_meeting: Optional[Dict[str, Any]] = Field(None, description="下一个会议")
    available_until: Optional[datetime] = Field(None, description="可用截止时间")
    next_available_time: Optional[datetime] = Field(None, description="下次可用时间")
    
    # 联系方式
    preferred_contact_method: str = Field(..., description="首选联系方式")
    phone_number: str = Field(..., description="电话号码")
    email: str = Field(..., description="邮箱地址")
    wechat_id: Optional[str] = Field(None, description="微信号")
    
    # 代理人信息
    delegate_contact: Optional[Dict[str, Any]] = Field(None, description="代理联系人")
    
    # 访客接待偏好
    preferred_meeting_room: Optional[str] = Field(None, description="偏好会议室")
    max_visitors_per_meeting: int = Field(default=10, description="单次接待访客上限")
    
    last_update_time: datetime = Field(default_factory=datetime.now, description="信息更新时间")


class MeetingRoomDTO(BaseModel):
    """会议室DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    room_id: int = Field(..., description="会议室ID")
    room_name: str = Field(..., description="会议室名称")
    room_code: str = Field(..., description="会议室编码")
    location: str = Field(..., description="会议室位置")
    floor: str = Field(..., description="楼层")
    
    # 容量信息
    capacity: int = Field(..., description="容纳人数")
    available_seats: int = Field(..., description="当前可用座位数")
    
    # 设备配置
    equipment: List[str] = Field(default_factory=list, description="设备清单")
    has_projector: bool = Field(default=False, description="是否有投影仪")
    has_whiteboard: bool = Field(default=False, description="是否有白板")
    has_video_conference: bool = Field(default=False, description="是否支持视频会议")
    has_audio_system: bool = Field(default=False, description="是否有音响系统")
    wifi_access: bool = Field(default=True, description="是否有WiFi")
    
    # 可用性状态
    is_available: bool = Field(..., description="当前是否可用")
    availability_periods: List[Dict[str, Any]] = Field(default_factory=list, description="可用时间段")
    
    # 预定信息
    current_booking: Optional[Dict[str, Any]] = Field(None, description="当前预定信息")
    next_booking: Optional[Dict[str, Any]] = Field(None, description="下一个预定")
    
    # 房间状态
    room_status: str = Field(..., description="房间状态: available|occupied|maintenance|reserved")
    temperature: Optional[float] = Field(None, description="室内温度")
    lighting_status: str = Field(default="normal", description="照明状态")
    
    # 预定限制
    booking_restrictions: List[str] = Field(default_factory=list, description="预定限制")
    advance_booking_required: bool = Field(default=False, description="是否需要提前预定")
    min_booking_duration: int = Field(default=30, description="最小预定时长（分钟）")
    max_booking_duration: int = Field(default=480, description="最大预定时长（分钟）")
    
    last_update_time: datetime = Field(default_factory=datetime.now, description="状态更新时间")


class MeetingRoomBookingDTO(BaseModel):
    """会议室预定DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    booking_id: str = Field(..., description="预定ID")
    room_id: int = Field(..., description="会议室ID")
    room_name: str = Field(..., description="会议室名称")
    
    # 预定时间
    booking_date: date = Field(..., description="预定日期")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    duration_minutes: int = Field(..., description="持续时长（分钟）")
    
    # 预定人信息
    booker: str = Field(..., description="预定人ID")
    booker_name: str = Field(..., description="预定人姓名")
    booker_phone: str = Field(..., description="预定人电话")
    
    # 会议信息
    meeting_title: str = Field(..., description="会议主题")
    meeting_type: str = Field(..., description="会议类型: internal|external|interview|training")
    attendee_count: int = Field(..., description="参会人数")
    visitor_count: int = Field(default=0, description="访客人数")
    
    # 访客信息
    visitor_details: List[Dict[str, Any]] = Field(default_factory=list, description="访客详细信息")
    
    # 设备需求
    equipment_requirements: List[str] = Field(default_factory=list, description="设备需求")
    catering_required: bool = Field(default=False, description="是否需要茶水服务")
    special_setup: Optional[str] = Field(None, description="特殊布置要求")
    
    # 预定状态
    booking_status: str = Field(..., description="预定状态: confirmed|pending|cancelled")
    confirmation_time: Optional[datetime] = Field(None, description="确认时间")
    cancellation_reason: Optional[str] = Field(None, description="取消原因")
    
    # 准备状态
    room_prepared: bool = Field(default=False, description="房间是否已准备")
    equipment_checked: bool = Field(default=False, description="设备是否已检查")
    catering_arranged: bool = Field(default=False, description="茶水是否已安排")
    
    # 元数据
    booking_time: datetime = Field(default_factory=datetime.now, description="预定时间")
    last_modified_time: datetime = Field(default_factory=datetime.now, description="最后修改时间")
    receptionist: str = Field(..., description="接待员ID")
    
    remarks: Optional[str] = Field(None, description="备注信息")


class ReceptionVisitorInfoDTO(BaseModel):
    """前台访客信息DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    visitor_id: int = Field(..., description="访客ID")
    name: str = Field(..., description="访客姓名")
    phone: str = Field(..., description="访客电话")
    id_number: str = Field(..., description="身份证号")
    company: Optional[str] = Field(None, description="公司名称")
    position: Optional[str] = Field(None, description="职位")
    
    # 访问信息
    visit_purpose: str = Field(..., description="访问目的")
    visit_date: date = Field(..., description="访问日期")
    visit_time_start: time = Field(..., description="访问开始时间")
    visit_time_end: time = Field(..., description="访问结束时间")
    expected_duration: int = Field(..., description="预计停留时长（分钟）")
    
    # 被访人信息
    employee_name: str = Field(..., description="被访人姓名")
    employee_phone: str = Field(..., description="被访人电话")
    employee_email: str = Field(..., description="被访人邮箱")
    department_name: str = Field(..., description="被访人部门")
    office_location: Optional[str] = Field(None, description="办公位置")
    
    # 审批信息
    approval_status: str = Field(..., description="审批状态")
    approved_by: Optional[str] = Field(None, description="审批人")
    approval_time: Optional[datetime] = Field(None, description="审批时间")
    approval_notes: Optional[str] = Field(None, description="审批备注")
    
    # 访问权限
    access_areas: List[str] = Field(default_factory=list, description="可访问区域")
    access_restrictions: List[str] = Field(default_factory=list, description="访问限制")
    escort_required: bool = Field(default=False, description="是否需要陪同")
    
    # 历史访问记录
    previous_visits_count: int = Field(default=0, description="历史访问次数")
    last_visit_date: Optional[date] = Field(None, description="最后访问日期")
    visit_frequency: str = Field(default="first_time", description="访问频率")
    
    # 特殊标记
    vip_status: bool = Field(default=False, description="是否为VIP访客")
    security_clearance_level: str = Field(default="standard", description="安全等级")
    blacklist_status: bool = Field(default=False, description="是否在黑名单")
    
    # 偏好设置
    language_preference: Optional[str] = Field(None, description="语言偏好")
    accessibility_needs: List[str] = Field(default_factory=list, description="无障碍需求")
    dietary_restrictions: List[str] = Field(default_factory=list, description="饮食限制")
    
    # 元数据
    registration_time: datetime = Field(..., description="注册时间")
    last_update_time: datetime = Field(..., description="最后更新时间")


class VisitorFeedbackDTO(BaseModel):
    """访客反馈DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    feedback_id: str = Field(..., description="反馈ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visit_date: date = Field(..., description="访问日期")
    
    # 整体评价
    overall_satisfaction: FeedbackRating = Field(..., description="整体满意度")
    overall_comments: Optional[str] = Field(None, description="整体评价")
    
    # 分项评价
    reception_service_rating: FeedbackRating = Field(..., description="前台服务评分")
    facility_rating: FeedbackRating = Field(..., description="设施环境评分")
    security_process_rating: FeedbackRating = Field(..., description="安保流程评分")
    waiting_experience_rating: FeedbackRating = Field(..., description="等候体验评分")
    
    # 具体反馈
    positive_aspects: List[str] = Field(default_factory=list, description="积极方面")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议")
    
    # 服务评价
    reception_staff_professional: bool = Field(default=True, description="前台人员是否专业")
    check_in_process_smooth: bool = Field(default=True, description="签到流程是否顺畅")
    waiting_area_comfortable: bool = Field(default=True, description="等候区是否舒适")
    directions_clear: bool = Field(default=True, description="指引是否清晰")
    
    # 推荐意愿
    would_recommend: bool = Field(default=True, description="是否愿意推荐")
    likelihood_to_return: int = Field(..., description="再次访问可能性 1-5分", ge=1, le=5)
    
    # 反馈收集信息
    feedback_method: str = Field(..., description="反馈收集方式: face_to_face|mobile|email|survey")
    collector: str = Field(..., description="收集人员ID")
    collection_time: datetime = Field(default_factory=datetime.now, description="收集时间")
    
    # 联系信息（可选）
    contact_for_follow_up: bool = Field(default=False, description="是否同意后续联系")
    preferred_contact_method: Optional[str] = Field(None, description="偏好联系方式")


class VisitorServiceRequestDTO(BaseModel):
    """访客服务请求DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    request_id: str = Field(..., description="服务请求ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visitor_phone: str = Field(..., description="访客电话")
    
    # 服务请求信息
    service_type: ServiceRequestType = Field(..., description="服务类型")
    request_title: str = Field(..., description="请求标题")
    request_description: str = Field(..., description="详细描述")
    urgency_level: str = Field(..., description="紧急程度: low|medium|high|urgent")
    
    # 位置信息
    request_location: str = Field(..., description="请求位置")
    visitor_current_location: Optional[str] = Field(None, description="访客当前位置")
    
    # 服务细节
    service_details: Dict[str, Any] = Field(default_factory=dict, description="服务具体详情")
    expected_completion_time: Optional[datetime] = Field(None, description="期望完成时间")
    
    # 请求状态
    request_status: ServiceRequestStatus = Field(..., description="请求状态")
    submitted_time: datetime = Field(default_factory=datetime.now, description="提交时间")
    
    # 处理信息
    assigned_to: Optional[str] = Field(None, description="分配给")
    handler_name: Optional[str] = Field(None, description="处理人姓名")
    handler_phone: Optional[str] = Field(None, description="处理人电话")
    estimated_response_time: Optional[int] = Field(None, description="预计响应时间（分钟）")
    
    # 处理过程
    processing_notes: List[Dict[str, Any]] = Field(default_factory=list, description="处理记录")
    start_processing_time: Optional[datetime] = Field(None, description="开始处理时间")
    completion_time: Optional[datetime] = Field(None, description="完成时间")
    
    # 结果信息
    resolution_summary: Optional[str] = Field(None, description="解决方案摘要")
    visitor_satisfaction: Optional[FeedbackRating] = Field(None, description="访客满意度")
    follow_up_required: bool = Field(default=False, description="是否需要后续跟进")
    
    # 费用信息
    service_cost: Optional[float] = Field(None, description="服务费用")
    payment_method: Optional[str] = Field(None, description="付费方式")
    
    # 元数据
    reception_desk: str = Field(..., description="受理前台")
    handler: str = Field(..., description="处理人员ID")


class WaitingAreaStatusDTO(BaseModel):
    """等候区状态DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    area_id: str = Field(..., description="等候区ID")
    area_name: str = Field(..., description="等候区名称")
    location: str = Field(..., description="位置")
    floor: str = Field(..., description="楼层")
    
    # 容量信息
    total_seats: int = Field(..., description="总座位数")
    occupied_seats: int = Field(..., description="已占用座位数")
    available_seats: int = Field(..., description="可用座位数")
    occupancy_rate: float = Field(..., description="占用率", ge=0, le=100)
    
    # 当前等候访客
    waiting_visitors: List[Dict[str, Any]] = Field(default_factory=list, description="等候访客列表")
    average_wait_time: Optional[int] = Field(None, description="平均等候时间（分钟）")
    
    # 环境状态
    temperature: Optional[float] = Field(None, description="温度")
    humidity: Optional[float] = Field(None, description="湿度")
    air_quality: Optional[str] = Field(None, description="空气质量")
    noise_level: Optional[str] = Field(None, description="噪音水平")
    
    # 设施状态
    wifi_available: bool = Field(default=True, description="WiFi是否可用")
    charging_stations: int = Field(default=0, description="充电站数量")
    reading_materials: bool = Field(default=True, description="是否有阅读材料")
    refreshments: bool = Field(default=True, description="是否有茶水")
    
    # 服务状态
    staff_on_duty: bool = Field(default=True, description="是否有工作人员值班")
    cleaning_status: str = Field(default="clean", description="清洁状态")
    maintenance_required: bool = Field(default=False, description="是否需要维护")
    
    # 统计信息
    daily_visitor_count: int = Field(default=0, description="今日访客数量")
    peak_occupancy_time: Optional[time] = Field(None, description="高峰占用时段")
    
    last_update_time: datetime = Field(default_factory=datetime.now, description="状态更新时间")


class DailyReceptionStatisticsDTO(BaseModel):
    """前台日报统计DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    statistics_date: date = Field(..., description="统计日期")
    reception_desk: str = Field(..., description="前台位置")
    
    # 访客统计
    total_visitors: int = Field(default=0, description="总访客数")
    successful_checkins: int = Field(default=0, description="成功签到数")
    failed_checkins: int = Field(default=0, description="失败签到数")
    vip_visitors: int = Field(default=0, description="VIP访客数")
    first_time_visitors: int = Field(default=0, description="首次访客数")
    returning_visitors: int = Field(default=0, description="回访访客数")
    
    # 时间分布
    peak_hours: List[Dict[str, Any]] = Field(default_factory=list, description="高峰时段")
    average_wait_time: float = Field(default=0.0, description="平均等候时间（分钟）")
    longest_wait_time: float = Field(default=0.0, description="最长等候时间（分钟）")
    
    # 服务统计
    total_service_requests: int = Field(default=0, description="总服务请求数")
    completed_service_requests: int = Field(default=0, description="已完成服务请求数")
    average_service_response_time: float = Field(default=0.0, description="平均服务响应时间（分钟）")
    
    # 会议室统计
    meeting_room_bookings: int = Field(default=0, description="会议室预定数")
    successful_room_arrangements: int = Field(default=0, description="成功安排会议室数")
    
    # 满意度统计
    feedback_count: int = Field(default=0, description="反馈收集数")
    average_satisfaction_score: float = Field(default=0.0, description="平均满意度评分", ge=0, le=5)
    satisfaction_distribution: Dict[str, int] = Field(default_factory=dict, description="满意度分布")
    
    # 问题统计
    total_issues: int = Field(default=0, description="总问题数")
    resolved_issues: int = Field(default=0, description="已解决问题数")
    escalated_issues: int = Field(default=0, description="上升问题数")
    
    # 人员统计
    reception_staff_count: int = Field(default=0, description="前台人员数量")
    staff_utilization_rate: float = Field(default=0.0, description="人员利用率", ge=0, le=100)
    
    # 资源利用
    waiting_area_peak_occupancy: float = Field(default=0.0, description="等候区峰值占用率", ge=0, le=100)
    equipment_usage_rate: float = Field(default=0.0, description="设备使用率", ge=0, le=100)
    
    # 生成信息
    generated_by: str = Field(..., description="统计生成人")
    generation_time: datetime = Field(default_factory=datetime.now, description="生成时间")
    
    # 备注和建议
    summary_notes: Optional[str] = Field(None, description="总结备注")
    improvement_recommendations: List[str] = Field(default_factory=list, description="改进建议") 