"""
门岗放行系统 Schema 定义
包含门岗验证、访客入园记录等相关数据传输对象
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from enum import Enum

from app.api.models.base_response import BaseResponseModel


# 枚举定义
class VerificationMethod(str, Enum):
    """验证方法枚举"""
    QR_CODE = "qr_code"
    ID_CARD = "id_card" 
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    SMS_OTP = "sms_otp"


class VerificationStatus(str, Enum):
    """验证状态枚举"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"


class EntryStatus(str, Enum):
    """入园状态枚举"""
    ENTERED = "entered"
    WAITING = "waiting"
    DENIED = "denied"
    EXITED = "exited"


# 门岗验证相关 Schema
class GateVerificationRequestSchema(BaseModel):
    """门岗验证请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    device_id: str = Field(..., description="设备ID")
    verification_method: VerificationMethod = Field(..., description="验证方法")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    offline_mode: bool = Field(False, description="是否离线模式")
    emergency_override: bool = Field(False, description="是否应急覆盖")

    @validator('verification_data')
    def validate_verification_data(cls, v, values):
        """验证数据格式验证"""
        method = values.get('verification_method')
        
        if method == VerificationMethod.QR_CODE:
            if 'qr_code' not in v:
                raise ValueError("二维码验证需要qr_code字段")
        elif method == VerificationMethod.ID_CARD:
            if 'id_number' not in v:
                raise ValueError("身份证验证需要id_number字段")
        elif method == VerificationMethod.FACE_RECOGNITION:
            if 'face_image' not in v:
                raise ValueError("人脸识别需要face_image字段")
        elif method == VerificationMethod.SMS_OTP:
            if 'otp_code' not in v:
                raise ValueError("短信验证需要otp_code字段")
        
        return v


class GateVerificationResponseSchema(BaseResponseModel):
    """门岗验证响应Schema"""
    verification_id: str = Field(..., description="验证记录ID")
    access_granted: bool = Field(..., description="是否允许通行")
    visitor_info: Dict[str, Any] = Field(..., description="访客信息")
    verification_time: datetime = Field(..., description="验证时间")
    confidence_score: Optional[float] = Field(None, description="验证置信度")
    failure_reason: Optional[str] = Field(None, description="失败原因")
    security_alerts: List[str] = Field(default=[], description="安全警告")
    next_actions: List[str] = Field(default=[], description="后续操作建议")


class VisitorEntryRequestSchema(BaseModel):
    """访客入园请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    gate_id: str = Field(..., description="门岗ID")
    entry_photo_url: Optional[str] = Field(None, description="入园照片URL")
    badge_number: Optional[str] = Field(None, description="徽章号码")
    vehicle_plate: Optional[str] = Field(None, description="车牌号")
    temperature_check: Optional[float] = Field(None, description="体温检测", ge=35.0, le=42.0)
    health_check_passed: bool = Field(True, description="健康检查是否通过")
    special_notes: Optional[str] = Field(None, description="特殊备注")
    entry_channel: Optional[str] = Field("main", description="入园通道")


class VisitorEntryResponseSchema(BaseResponseModel):
    """访客入园响应Schema"""
    entry_id: str = Field(..., description="入园记录ID")
    visitor_id: int = Field(..., description="访客ID")
    entry_time: datetime = Field(..., description="入园时间")
    badge_number: Optional[str] = Field(None, description="分配的徽章号码")
    expected_exit_time: Optional[datetime] = Field(None, description="预期离园时间")
    entry_status: EntryStatus = Field(..., description="入园状态")
    qr_code_url: Optional[str] = Field(None, description="访客二维码URL")


class TodayVisitorsRequestSchema(BaseModel):
    """今日访客查询请求Schema"""
    gate_id: str = Field(..., description="门岗ID")
    status_filter: Optional[List[EntryStatus]] = Field(None, description="状态筛选")
    search_keyword: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="页面大小", ge=1, le=100)


class TodayVisitorItemSchema(BaseModel):
    """今日访客条目Schema"""
    visitor_id: int = Field(..., description="访客ID")
    name: str = Field(..., description="姓名")
    phone: str = Field(..., description="电话")
    company: Optional[str] = Field(None, description="公司")
    entry_time: Optional[datetime] = Field(None, description="入园时间")
    exit_time: Optional[datetime] = Field(None, description="离园时间")
    status: EntryStatus = Field(..., description="当前状态")
    host_name: Optional[str] = Field(None, description="接待人")
    verification_method: Optional[str] = Field(None, description="验证方式")
    badge_number: Optional[str] = Field(None, description="徽章号码")


class TodayVisitorsResponseSchema(BaseResponseModel):
    """今日访客查询响应Schema"""
    visitors: List[TodayVisitorItemSchema] = Field(..., description="访客列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="页面大小")
    summary: Dict[str, Any] = Field(..., description="统计摘要")


# 访客缓存相关 Schema
class VisitorCacheRequestSchema(BaseModel):
    """访客缓存请求Schema"""
    device_id: str = Field(..., description="设备ID")
    cache_type: str = Field("today", description="缓存类型")
    refresh: bool = Field(False, description="是否强制刷新")


class VisitorCacheItemSchema(BaseModel):
    """访客缓存条目Schema"""
    visitor_id: int = Field(..., description="访客ID")
    name: str = Field(..., description="姓名")
    id_card: str = Field(..., description="身份证号")
    phone: str = Field(..., description="电话")
    company: Optional[str] = Field(None, description="公司")
    visit_purpose: str = Field(..., description="来访目的")
    host_name: str = Field(..., description="接待人")
    expected_arrival: datetime = Field(..., description="预期到达时间")
    status: str = Field(..., description="状态")
    qr_code: Optional[str] = Field(None, description="二维码")
    verification_required: List[str] = Field(..., description="需要的验证方式")


class VisitorCacheResponseSchema(BaseResponseModel):
    """访客缓存响应Schema"""
    cache_time: datetime = Field(..., description="缓存时间")
    visitors: List[VisitorCacheItemSchema] = Field(..., description="访客缓存列表")
    total_count: int = Field(..., description="总数量")
    device_id: str = Field(..., description="设备ID")
    cache_validity: int = Field(..., description="缓存有效期(分钟)")


# 离线验证相关 Schema
class OfflineVerificationRequestSchema(BaseModel):
    """离线验证请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    device_id: str = Field(..., description="设备ID")
    verification_method: VerificationMethod = Field(..., description="验证方法")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    offline_time: datetime = Field(..., description="离线验证时间")
    device_timestamp: datetime = Field(..., description="设备时间戳")
    sync_priority: int = Field(1, description="同步优先级", ge=1, le=5)


class OfflineVerificationSyncRequestSchema(BaseModel):
    """离线验证同步请求Schema"""
    device_id: str = Field(..., description="设备ID")
    offline_verifications: List[OfflineVerificationRequestSchema] = Field(..., description="离线验证列表")
    sync_timestamp: datetime = Field(..., description="同步时间戳")


class OfflineVerificationSyncResponseSchema(BaseResponseModel):
    """离线验证同步响应Schema"""
    sync_id: str = Field(..., description="同步ID")
    processed_count: int = Field(..., description="处理数量")
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    conflicts: List[Dict[str, Any]] = Field(default=[], description="冲突记录")
    sync_time: datetime = Field(..., description="同步时间")


# 应急处理相关 Schema
class EmergencyVerificationRequestSchema(BaseModel):
    """应急验证请求Schema"""
    emergency_type: str = Field(..., description="应急类型")
    reason: str = Field(..., description="应急原因")
    affected_devices: List[str] = Field(..., description="受影响设备列表")
    operation_type: str = Field(..., description="操作类型")
    operator: str = Field(..., description="操作员")
    emergency_level: int = Field(1, description="应急等级", ge=1, le=5)
    duration_minutes: Optional[int] = Field(None, description="持续时间(分钟)")


class EmergencyVerificationResponseSchema(BaseResponseModel):
    """应急验证响应Schema"""
    emergency_id: str = Field(..., description="应急处理ID")
    activated_at: datetime = Field(..., description="激活时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    affected_devices: List[str] = Field(..., description="受影响设备")
    emergency_procedures: List[str] = Field(..., description="应急程序")
    operation_status: str = Field(..., description="操作状态")


# 验证统计相关 Schema
class GateStatisticsRequestSchema(BaseModel):
    """门岗统计请求Schema"""
    gate_id: Optional[str] = Field(None, description="门岗ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    group_by: str = Field("day", description="分组方式")


class GateStatisticsResponseSchema(BaseResponseModel):
    """门岗统计响应Schema"""
    total_verifications: int = Field(..., description="总验证次数")
    success_verifications: int = Field(..., description="成功验证次数")
    failed_verifications: int = Field(..., description="失败验证次数")
    success_rate: float = Field(..., description="成功率")
    method_statistics: Dict[str, int] = Field(..., description="验证方法统计")
    hourly_distribution: Dict[str, int] = Field(..., description="小时分布")
    peak_hours: List[str] = Field(..., description="高峰时段")
    average_verification_time: float = Field(..., description="平均验证时间(秒)")


# 门岗状态相关 Schema
class GateStatusRequestSchema(BaseModel):
    """门岗状态请求Schema"""
    gate_id: str = Field(..., description="门岗ID")


class GateStatusResponseSchema(BaseResponseModel):
    """门岗状态响应Schema"""
    gate_id: str = Field(..., description="门岗ID")
    status: str = Field(..., description="门岗状态")
    online_since: Optional[datetime] = Field(None, description="在线时间")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳")
    current_visitors: int = Field(..., description="当前访客数")
    today_entries: int = Field(..., description="今日入园数")
    device_health: Dict[str, Any] = Field(..., description="设备健康状态")
    active_alerts: List[str] = Field(default=[], description="活跃警告")


# 访客退园相关 Schema  
class VisitorExitRequestSchema(BaseModel):
    """访客退园请求Schema"""
    visitor_id: int = Field(..., description="访客ID")
    gate_id: str = Field(..., description="门岗ID")
    exit_method: str = Field("manual", description="退园方式")
    badge_returned: bool = Field(True, description="徽章是否归还")
    satisfaction_rating: Optional[int] = Field(None, description="满意度评分", ge=1, le=5)
    feedback: Optional[str] = Field(None, description="反馈意见")


class VisitorExitResponseSchema(BaseResponseModel):
    """访客退园响应Schema"""
    exit_id: str = Field(..., description="退园记录ID")
    visitor_id: int = Field(..., description="访客ID")
    exit_time: datetime = Field(..., description="退园时间")
    visit_duration: int = Field(..., description="访问时长(分钟)")
    exit_status: str = Field(..., description="退园状态")
    final_notes: Optional[str] = Field(None, description="最终备注") 