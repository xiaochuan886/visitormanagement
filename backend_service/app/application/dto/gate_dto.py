"""
门岗放行系统数据传输对象
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class VerificationMethod(str, Enum):
    """验证方式枚举"""
    QR_CODE = "qr_code"
    ID_CARD = "id_card" 
    FACE_RECOGNITION = "face_recognition"
    MANUAL = "manual"
    PHONE_OTP = "phone_otp"


class VerificationStatus(str, Enum):
    """验证状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    BLACKLIST = "blacklist"
    EXPIRED = "expired"


class AlertType(str, Enum):
    """告警类型枚举"""
    BLACKLIST = "blacklist"
    UNAUTHORIZED = "unauthorized"
    SYSTEM_ERROR = "system_error"
    DEVICE_FAILURE = "device_failure"
    EMERGENCY = "emergency"


class DeviceStatus(str, Enum):
    """设备状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline" 
    MAINTENANCE = "maintenance"
    ERROR = "error"


class GateAccessLevel(str, Enum):
    """门岗访问级别枚举"""
    BASIC = "basic"
    STANDARD = "standard" 
    VIP = "vip"
    EMERGENCY = "emergency"
    RESTRICTED = "restricted"


class GateVerificationDTO(BaseModel):
    """门岗验证结果DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    verification_id: str = Field(..., description="验证记录ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visitor_phone: str = Field(..., description="访客电话")
    verification_method: VerificationMethod = Field(..., description="验证方式")
    verification_status: VerificationStatus = Field(..., description="验证状态")
    confidence_score: float = Field(default=0.0, description="验证置信度 0-100", ge=0, le=100)
    verification_data: Optional[Dict[str, Any]] = Field(None, description="验证原始数据")
    blacklist_check: bool = Field(default=False, description="是否通过黑名单检查")
    access_permissions: List[str] = Field(default_factory=list, description="访问权限区域")
    valid_until: datetime = Field(..., description="权限有效期")
    gate_id: str = Field(..., description="门岗设备ID")
    operator: str = Field(..., description="操作员ID")
    verification_time: datetime = Field(default_factory=datetime.now, description="验证时间")
    remarks: Optional[str] = Field(None, description="备注信息")


class VisitorEntryDTO(BaseModel):
    """访客入园登记DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    entry_id: str = Field(..., description="入园记录ID")
    visitor_id: int = Field(..., description="访客ID")
    visitor_name: str = Field(..., description="访客姓名")
    visitor_badge_number: Optional[str] = Field(None, description="访客证号码")
    entry_time: datetime = Field(default_factory=datetime.now, description="入园时间")
    gate_id: str = Field(..., description="入园门岗ID")
    entry_photo_url: Optional[str] = Field(None, description="入园现场照片URL")
    
    # 车辆信息
    vehicle_info: Optional[Dict[str, Any]] = Field(None, description="车辆信息")
    vehicle_plate: Optional[str] = Field(None, description="车牌号")
    parking_spot: Optional[str] = Field(None, description="停车位")
    
    # 权限信息
    access_areas: List[str] = Field(default_factory=list, description="可访问区域")
    access_valid_until: datetime = Field(..., description="访问权限截止时间")
    
    # 安全检查
    security_check_passed: bool = Field(default=True, description="安全检查是否通过")
    temperature_check: Optional[float] = Field(None, description="体温检测结果")
    health_code_status: Optional[str] = Field(None, description="健康码状态")
    
    operator: str = Field(..., description="操作员ID")
    remarks: Optional[str] = Field(None, description="备注")


class TodayVisitorsCacheDTO(BaseModel):
    """今日访客缓存数据DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    visitor_id: int = Field(..., description="访客ID")
    name: str = Field(..., description="访客姓名")
    phone: str = Field(..., description="访客电话")
    id_number: str = Field(..., description="身份证号")
    qr_code: str = Field(..., description="二维码")
    
    # 访问信息
    visit_date: date = Field(..., description="访问日期")
    visit_time_start: time = Field(..., description="访问开始时间")
    visit_time_end: time = Field(..., description="访问结束时间")
    visit_purpose: str = Field(..., description="访问目的")
    
    # 被访人信息
    employee_name: str = Field(..., description="被访人姓名")
    employee_phone: str = Field(..., description="被访人电话")
    department_name: str = Field(..., description="被访人部门")
    
    # 权限信息
    access_areas: List[str] = Field(default_factory=list, description="可访问区域")
    approval_status: str = Field(..., description="审批状态")
    
    # 缓存元数据
    cache_version: str = Field(..., description="缓存版本")
    last_sync_time: datetime = Field(..., description="最后同步时间")


class OfflineVerificationDTO(BaseModel):
    """离线验证记录DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    offline_id: str = Field(..., description="离线记录ID")
    visitor_id: int = Field(..., description="访客ID")
    verification_method: VerificationMethod = Field(..., description="验证方式")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    gate_id: str = Field(..., description="门岗设备ID")
    offline_time: datetime = Field(..., description="离线验证时间")
    sync_status: str = Field(default="pending", description="同步状态")
    operator: str = Field(..., description="操作员ID")
    device_timestamp: datetime = Field(..., description="设备时间戳")


class GateStatusDTO(BaseModel):
    """门岗状态DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    gate_id: str = Field(..., description="门岗ID")
    gate_name: str = Field(..., description="门岗名称")
    location: str = Field(..., description="门岗位置")
    status: DeviceStatus = Field(..., description="运行状态")
    
    # 实时统计
    today_visitors_count: int = Field(default=0, description="今日访客数量")
    current_queue_length: int = Field(default=0, description="当前排队人数")
    in_park_visitors_count: int = Field(default=0, description="园区内访客数量")
    
    # 设备健康状态
    device_health_score: float = Field(default=100.0, description="设备健康度评分", ge=0, le=100)
    last_heartbeat: datetime = Field(..., description="最后心跳时间")
    network_status: str = Field(default="connected", description="网络连接状态")
    
    # 功能模块状态
    qr_scanner_status: str = Field(default="normal", description="二维码扫描器状态")
    id_reader_status: str = Field(default="normal", description="身份证读卡器状态")
    face_camera_status: str = Field(default="normal", description="人脸识别摄像头状态")
    printer_status: str = Field(default="normal", description="打印机状态")
    
    operator_on_duty: Optional[str] = Field(None, description="当班操作员")
    last_update_time: datetime = Field(default_factory=datetime.now, description="状态更新时间")


class EmergencyOpenDTO(BaseModel):
    """紧急开放DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    emergency_id: str = Field(..., description="紧急事件ID")
    emergency_type: str = Field(..., description="紧急事件类型")
    affected_gates: List[str] = Field(..., description="影响的门岗列表")
    emergency_reason: str = Field(..., description="紧急原因")
    duration_minutes: int = Field(..., description="开放持续时间（分钟）")
    authorized_by: str = Field(..., description="授权人员")
    operator: str = Field(..., description="操作员")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    expected_end_time: datetime = Field(..., description="预期结束时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    emergency_contacts_notified: List[str] = Field(default_factory=list, description="已通知的紧急联系人")


class GateDeviceStatusDTO(BaseModel):
    """门岗设备状态DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    device_type: str = Field(..., description="设备类型")
    status: DeviceStatus = Field(..., description="设备状态")
    
    # 系统信息
    cpu_usage: float = Field(default=0.0, description="CPU使用率", ge=0, le=100)
    memory_usage: float = Field(default=0.0, description="内存使用率", ge=0, le=100)
    disk_usage: float = Field(default=0.0, description="磁盘使用率", ge=0, le=100)
    temperature: Optional[float] = Field(None, description="设备温度")
    
    # 网络状态
    network_latency: Optional[float] = Field(None, description="网络延迟（毫秒）")
    network_quality: Optional[str] = Field(None, description="网络质量")
    
    # 组件状态
    camera_status: str = Field(default="normal", description="摄像头状态")
    scanner_status: str = Field(default="normal", description="扫描器状态")
    printer_status: str = Field(default="normal", description="打印机状态")
    
    # 软件版本
    software_version: str = Field(..., description="软件版本")
    last_update_time: datetime = Field(..., description="最后更新时间")
    
    # 错误信息
    error_codes: List[str] = Field(default_factory=list, description="错误代码列表")
    error_messages: List[str] = Field(default_factory=list, description="错误信息列表")
    
    # 维护信息
    last_maintenance_time: Optional[datetime] = Field(None, description="最后维护时间")
    next_maintenance_time: Optional[datetime] = Field(None, description="下次维护时间")


class SecurityAlertDTO(BaseModel):
    """安全告警DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    alert_id: str = Field(..., description="告警ID")
    alert_type: AlertType = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度: low|medium|high|critical")
    gate_id: str = Field(..., description="门岗设备ID")
    visitor_id: Optional[int] = Field(None, description="相关访客ID")
    
    alert_title: str = Field(..., description="告警标题")
    alert_message: str = Field(..., description="告警详细信息")
    alert_data: Dict[str, Any] = Field(default_factory=dict, description="告警原始数据")
    
    reporter: str = Field(..., description="报告人")
    report_time: datetime = Field(default_factory=datetime.now, description="报告时间")
    
    # 处理状态
    status: str = Field(default="open", description="处理状态: open|investigating|resolved|false_positive")
    assigned_to: Optional[str] = Field(None, description="分配给")
    resolution_notes: Optional[str] = Field(None, description="处理备注")
    resolved_time: Optional[datetime] = Field(None, description="解决时间")
    
    # 自动处理
    auto_action_taken: Optional[str] = Field(None, description="自动采取的行动")
    requires_manual_review: bool = Field(default=True, description="是否需要人工审核")


class VisitorInParkDTO(BaseModel):
    """园区内访客DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    visitor_id: int = Field(..., description="访客ID")
    name: str = Field(..., description="访客姓名")
    phone: str = Field(..., description="访客电话")
    badge_number: Optional[str] = Field(None, description="访客证号码")
    
    # 入园信息
    entry_time: datetime = Field(..., description="入园时间")
    entry_gate: str = Field(..., description="入园门岗")
    
    # 当前状态
    current_location: Optional[str] = Field(None, description="当前位置")
    current_status: str = Field(..., description="当前状态: in_park|meeting|waiting")
    
    # 被访人信息
    employee_name: str = Field(..., description="被访人姓名")
    department_name: str = Field(..., description="被访人部门")
    
    # 权限信息
    access_areas: List[str] = Field(default_factory=list, description="可访问区域")
    access_expires: datetime = Field(..., description="权限过期时间")
    
    # 访问详情
    visit_purpose: str = Field(..., description="访问目的")
    expected_duration: int = Field(..., description="预期停留时长（分钟）")
    
    # 车辆信息
    vehicle_plate: Optional[str] = Field(None, description="车牌号")
    parking_spot: Optional[str] = Field(None, description="停车位")


class MultiVerificationRequestDTO(BaseModel):
    """多重验证请求DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    visitor_id: int = Field(..., description="访客ID")
    gate_id: str = Field(..., description="门岗设备ID")
    
    # 验证方法组合
    primary_method: VerificationMethod = Field(..., description="主要验证方式")
    secondary_methods: List[VerificationMethod] = Field(default_factory=list, description="辅助验证方式")
    
    # 验证数据
    qr_code_data: Optional[str] = Field(None, description="二维码数据")
    id_card_data: Optional[Dict[str, Any]] = Field(None, description="身份证数据")
    face_image_data: Optional[str] = Field(None, description="人脸图像数据（base64）")
    phone_otp: Optional[str] = Field(None, description="手机验证码")
    
    # 验证配置
    require_all_methods: bool = Field(default=False, description="是否要求所有方法都通过")
    confidence_threshold: float = Field(default=80.0, description="置信度阈值", ge=0, le=100)
    
    operator: str = Field(..., description="操作员ID")
    verification_timestamp: datetime = Field(default_factory=datetime.now, description="验证时间戳")


class FusionVerificationResultDTO(BaseModel):
    """融合验证结果DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    fusion_id: str = Field(..., description="融合验证ID")
    visitor_id: int = Field(..., description="访客ID")
    overall_status: VerificationStatus = Field(..., description="总体验证状态")
    overall_confidence: float = Field(..., description="总体置信度", ge=0, le=100)
    
    # 各方法验证结果
    method_results: List[Dict[str, Any]] = Field(default_factory=list, description="各验证方法结果")
    
    # 融合算法信息
    fusion_algorithm: str = Field(default="weighted_average", description="融合算法")
    weight_distribution: Dict[str, float] = Field(default_factory=dict, description="权重分布")
    
    # 决策信息
    recommendation: str = Field(..., description="推荐决策: allow|deny|manual_review")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict, description="置信度分解")
    
    gate_id: str = Field(..., description="门岗设备ID")
    fusion_time: datetime = Field(default_factory=datetime.now, description="融合时间")
    operator: str = Field(..., description="操作员ID") 