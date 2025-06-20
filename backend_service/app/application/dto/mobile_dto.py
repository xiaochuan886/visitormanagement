"""
移动端备用验证方案数据传输对象
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MobileDeviceType(str, Enum):
    """移动设备类型枚举"""
    ANDROID_TABLET = "android_tablet"
    IPAD = "ipad"
    ANDROID_PHONE = "android_phone"
    IPHONE = "iphone"
    WECHAT_MINIPROGRAM = "wechat_miniprogram"
    WEB_MOBILE = "web_mobile"


class SyncStatus(str, Enum):
    """同步状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class NetworkQuality(str, Enum):
    """网络质量枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    OFFLINE = "offline"


class EmergencyType(str, Enum):
    """应急类型枚举"""
    NETWORK_FAILURE = "network_failure"
    SYSTEM_MAINTENANCE = "system_maintenance"
    DEVICE_FAILURE = "device_failure"
    POWER_OUTAGE = "power_outage"
    SECURITY_INCIDENT = "security_incident"


class PhotoQuality(str, Enum):
    """照片质量枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    COMPRESSED = "compressed"


class MobileGateSyncDTO(BaseModel):
    """门岗移动端数据同步DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    sync_id: str = Field(..., description="同步记录ID")
    device_id: str = Field(..., description="移动设备ID")
    device_type: MobileDeviceType = Field(..., description="设备类型")
    gate_id: str = Field(..., description="门岗ID")
    
    # 同步时间信息
    sync_timestamp: datetime = Field(default_factory=datetime.now, description="同步时间戳")
    last_sync_time: Optional[datetime] = Field(None, description="上次同步时间")
    
    # 同步数据范围
    sync_date_from: date = Field(..., description="同步开始日期")
    sync_date_to: date = Field(..., description="同步结束日期")
    
    # 今日访客数据
    today_visitors_count: int = Field(default=0, description="今日访客总数")
    approved_visitors: List[Dict[str, Any]] = Field(default_factory=list, description="已审批访客列表")
    pending_visitors: List[Dict[str, Any]] = Field(default_factory=list, description="待审批访客列表")
    
    # 黑名单数据
    blacklist_entries: List[Dict[str, Any]] = Field(default_factory=list, description="黑名单条目")
    blacklist_version: str = Field(..., description="黑名单版本")
    
    # 配置数据
    gate_configuration: Dict[str, Any] = Field(default_factory=dict, description="门岗配置")
    verification_rules: Dict[str, Any] = Field(default_factory=dict, description="验证规则")
    
    # 同步状态
    sync_status: SyncStatus = Field(..., description="同步状态")
    data_size_kb: float = Field(default=0.0, description="数据大小（KB）")
    compression_ratio: float = Field(default=1.0, description="压缩比例")
    
    # 网络信息
    network_quality: NetworkQuality = Field(..., description="网络质量")
    download_speed_kbps: Optional[float] = Field(None, description="下载速度（KB/s）")
    
    # 错误信息
    error_code: Optional[str] = Field(None, description="错误代码")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    operator: str = Field(..., description="操作员ID")


class MobileQRVerificationDTO(BaseModel):
    """移动端二维码验证DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    verification_id: str = Field(..., description="验证ID")
    device_id: str = Field(..., description="移动设备ID")
    gate_id: str = Field(..., description="门岗ID")
    
    # 二维码信息
    qr_code_data: str = Field(..., description="二维码数据")
    qr_scan_timestamp: datetime = Field(..., description="扫描时间戳")
    qr_image_quality: PhotoQuality = Field(default=PhotoQuality.MEDIUM, description="二维码图像质量")
    
    # 验证结果
    visitor_id: Optional[int] = Field(None, description="访客ID")
    visitor_name: Optional[str] = Field(None, description="访客姓名")
    verification_success: bool = Field(..., description="验证是否成功")
    verification_message: str = Field(..., description="验证消息")
    
    # 访客信息
    visitor_phone: Optional[str] = Field(None, description="访客电话")
    visit_purpose: Optional[str] = Field(None, description="访问目的")
    employee_name: Optional[str] = Field(None, description="被访人姓名")
    
    # 权限信息
    access_granted: bool = Field(default=False, description="是否授予访问权限")
    access_areas: List[str] = Field(default_factory=list, description="允许访问区域")
    access_valid_until: Optional[datetime] = Field(None, description="权限有效期")
    
    # 安全检查
    blacklist_check_passed: bool = Field(default=True, description="黑名单检查是否通过")
    time_window_valid: bool = Field(default=True, description="时间窗口是否有效")
    area_permission_valid: bool = Field(default=True, description="区域权限是否有效")
    
    # 设备信息
    device_location: Optional[Dict[str, float]] = Field(None, description="设备位置（经纬度）")
    network_status: str = Field(..., description="网络连接状态")
    
    # 操作信息
    operator: str = Field(..., description="操作员ID")
    verification_timestamp: datetime = Field(default_factory=datetime.now, description="验证时间戳")
    
    # 备注
    remarks: Optional[str] = Field(None, description="备注信息")


class MobileVisitorInfoDTO(BaseModel):
    """移动端访客信息DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    visitor_id: int = Field(..., description="访客ID")
    qr_code: str = Field(..., description="二维码")
    
    # 基本信息
    name: str = Field(..., description="访客姓名")
    phone: str = Field(..., description="访客电话")
    company: Optional[str] = Field(None, description="公司名称")
    id_number_masked: str = Field(..., description="身份证号（掩码）")
    
    # 访问信息
    visit_date: date = Field(..., description="访问日期")
    visit_time_start: time = Field(..., description="访问开始时间")
    visit_time_end: time = Field(..., description="访问结束时间")
    visit_purpose: str = Field(..., description="访问目的")
    
    # 被访人信息
    employee_name: str = Field(..., description="被访人姓名")
    employee_phone_masked: str = Field(..., description="被访人电话（掩码）")
    department_name: str = Field(..., description="被访人部门")
    
    # 状态信息
    approval_status: str = Field(..., description="审批状态")
    visit_status: str = Field(..., description="访问状态")
    current_location: Optional[str] = Field(None, description="当前位置")
    
    # 权限信息
    access_areas: List[str] = Field(default_factory=list, description="可访问区域")
    access_restrictions: List[str] = Field(default_factory=list, description="访问限制")
    
    # 入园信息
    entry_time: Optional[datetime] = Field(None, description="入园时间")
    entry_gate: Optional[str] = Field(None, description="入园门岗")
    visitor_badge_number: Optional[str] = Field(None, description="访客证号码")
    
    # 照片信息
    photo_url: Optional[str] = Field(None, description="访客照片URL")
    photo_timestamp: Optional[datetime] = Field(None, description="照片时间戳")
    
    # 缓存信息
    cache_version: str = Field(..., description="缓存版本")
    last_update_time: datetime = Field(..., description="最后更新时间")


class MobileQuickCheckinDTO(BaseModel):
    """移动端快速签到DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    checkin_id: str = Field(..., description="签到ID")
    visitor_id: int = Field(..., description="访客ID")
    device_id: str = Field(..., description="移动设备ID")
    
    # 签到信息
    checkin_method: str = Field(..., description="签到方式: qr_scan|manual_entry|nfc")
    checkin_timestamp: datetime = Field(default_factory=datetime.now, description="签到时间戳")
    checkin_location: str = Field(..., description="签到位置")
    
    # 访客基本信息
    visitor_name: str = Field(..., description="访客姓名")
    visitor_phone: str = Field(..., description="访客电话")
    
    # 健康检查（简化版）
    health_declaration: bool = Field(default=True, description="健康声明")
    temperature_normal: bool = Field(default=True, description="体温正常")
    
    # 快速验证
    identity_verified: bool = Field(..., description="身份是否验证")
    access_authorized: bool = Field(..., description="访问是否授权")
    
    # 分配信息
    waiting_area: Optional[str] = Field(None, description="等候区域")
    seat_assignment: Optional[str] = Field(None, description="座位分配")
    
    # 通知状态
    host_notified: bool = Field(default=False, description="被访人是否已通知")
    notification_method: Optional[str] = Field(None, description="通知方式")
    
    # 设备信息
    device_battery_level: Optional[int] = Field(None, description="设备电量百分比", ge=0, le=100)
    network_quality: NetworkQuality = Field(..., description="网络质量")
    
    # 操作信息
    operator: str = Field(..., description="操作员ID")
    reception_desk: Optional[str] = Field(None, description="前台位置")
    
    # 签到结果
    checkin_success: bool = Field(..., description="签到是否成功")
    checkin_message: str = Field(..., description="签到结果消息")
    
    remarks: Optional[str] = Field(None, description="备注")


class MobileOfflineCacheDTO(BaseModel):
    """移动端离线缓存DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    cache_id: str = Field(..., description="缓存ID")
    device_id: str = Field(..., description="设备ID")
    cache_type: str = Field(..., description="缓存类型: visitor_data|blacklist|config")
    
    # 缓存范围
    cache_date: date = Field(..., description="缓存日期")
    cache_scope: str = Field(..., description="缓存范围: today|week|month")
    
    # 访客数据缓存
    cached_visitors: List[Dict[str, Any]] = Field(default_factory=list, description="缓存访客数据")
    visitor_count: int = Field(default=0, description="缓存访客数量")
    
    # 配置数据缓存
    verification_rules: Dict[str, Any] = Field(default_factory=dict, description="验证规则")
    area_permissions: Dict[str, Any] = Field(default_factory=dict, description="区域权限")
    blacklist_data: List[Dict[str, Any]] = Field(default_factory=list, description="黑名单数据")
    
    # 缓存元数据
    cache_size_mb: float = Field(default=0.0, description="缓存大小（MB）")
    compression_enabled: bool = Field(default=True, description="是否启用压缩")
    encryption_enabled: bool = Field(default=True, description="是否启用加密")
    
    # 有效性信息
    cache_created_time: datetime = Field(default_factory=datetime.now, description="缓存创建时间")
    cache_expires_time: datetime = Field(..., description="缓存过期时间")
    cache_version: str = Field(..., description="缓存版本")
    
    # 同步信息
    last_sync_time: Optional[datetime] = Field(None, description="上次同步时间")
    sync_required: bool = Field(default=False, description="是否需要同步")
    
    # 使用统计
    access_count: int = Field(default=0, description="访问次数")
    hit_rate: float = Field(default=0.0, description="命中率", ge=0, le=100)
    
    # 设备信息
    device_storage_available_mb: Optional[float] = Field(None, description="设备可用存储（MB）")
    device_memory_usage_mb: Optional[float] = Field(None, description="设备内存使用（MB）")


class MobileOfflineSyncDTO(BaseModel):
    """移动端离线数据同步DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    sync_session_id: str = Field(..., description="同步会话ID")
    device_id: str = Field(..., description="设备ID")
    
    # 离线期间数据
    offline_start_time: datetime = Field(..., description="离线开始时间")
    offline_end_time: datetime = Field(..., description="离线结束时间")
    offline_duration_minutes: int = Field(..., description="离线持续时间（分钟）")
    
    # 待同步数据
    pending_verifications: List[Dict[str, Any]] = Field(default_factory=list, description="待同步验证记录")
    pending_checkins: List[Dict[str, Any]] = Field(default_factory=list, description="待同步签到记录")
    pending_photos: List[Dict[str, Any]] = Field(default_factory=list, description="待同步照片")
    pending_logs: List[Dict[str, Any]] = Field(default_factory=list, description="待同步日志")
    
    # 数据统计
    total_records: int = Field(default=0, description="总记录数")
    successful_syncs: int = Field(default=0, description="成功同步数")
    failed_syncs: int = Field(default=0, description="失败同步数")
    
    # 同步过程
    sync_start_time: datetime = Field(default_factory=datetime.now, description="同步开始时间")
    sync_end_time: Optional[datetime] = Field(None, description="同步结束时间")
    sync_status: SyncStatus = Field(..., description="同步状态")
    
    # 冲突处理
    conflicts_detected: int = Field(default=0, description="检测到的冲突数")
    conflicts_resolved: int = Field(default=0, description="已解决的冲突数")
    conflict_resolution_strategy: str = Field(default="server_wins", description="冲突解决策略")
    
    # 网络信息
    network_quality_during_sync: NetworkQuality = Field(..., description="同步时网络质量")
    upload_speed_kbps: Optional[float] = Field(None, description="上传速度（KB/s）")
    
    # 错误信息
    error_details: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")
    retry_count: int = Field(default=0, description="重试次数")
    
    operator: str = Field(..., description="操作员ID")


class EmergencyVerificationDTO(BaseModel):
    """应急验证DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    emergency_id: str = Field(..., description="应急验证ID")
    device_id: str = Field(..., description="设备ID")
    gate_id: Optional[str] = Field(None, description="门岗ID")
    
    # 应急情况
    emergency_type: EmergencyType = Field(..., description="应急类型")
    emergency_reason: str = Field(..., description="应急原因")
    emergency_start_time: datetime = Field(..., description="应急开始时间")
    
    # 访客信息
    visitor_name: str = Field(..., description="访客姓名")
    visitor_phone: str = Field(..., description="访客电话")
    visitor_id_number: Optional[str] = Field(None, description="身份证号")
    visitor_company: Optional[str] = Field(None, description="公司名称")
    
    # 被访人信息
    employee_name: str = Field(..., description="被访人姓名")
    employee_phone: str = Field(..., description="被访人电话")
    department_name: str = Field(..., description="部门名称")
    
    # 验证方式
    verification_method: str = Field(..., description="验证方式: manual|phone_call|id_card|photo")
    manual_verification_reason: Optional[str] = Field(None, description="人工验证原因")
    
    # 授权信息
    authorized_by: str = Field(..., description="授权人员")
    authorization_level: str = Field(..., description="授权级别")
    temporary_access_granted: bool = Field(default=True, description="是否授予临时访问权限")
    
    # 限制条件
    access_duration_minutes: int = Field(..., description="访问时长限制（分钟）")
    escort_required: bool = Field(default=True, description="是否需要陪同")
    restricted_areas: List[str] = Field(default_factory=list, description="限制访问区域")
    
    # 风险评估
    risk_level: str = Field(..., description="风险等级: low|medium|high")
    risk_factors: List[str] = Field(default_factory=list, description="风险因素")
    mitigation_measures: List[str] = Field(default_factory=list, description="缓解措施")
    
    # 记录信息
    operator: str = Field(..., description="操作员ID")
    supervisor_approval: Optional[str] = Field(None, description="主管审批")
    verification_timestamp: datetime = Field(default_factory=datetime.now, description="验证时间戳")
    
    # 后续跟进
    follow_up_required: bool = Field(default=True, description="是否需要后续跟进")
    incident_report_generated: bool = Field(default=False, description="是否生成事件报告")
    
    remarks: str = Field(..., description="详细备注")


class MobileDeviceStatusDTO(BaseModel):
    """移动设备状态DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    device_type: MobileDeviceType = Field(..., description="设备类型")
    device_name: str = Field(..., description="设备名称")
    
    # 系统信息
    os_version: str = Field(..., description="操作系统版本")
    app_version: str = Field(..., description="应用程序版本")
    device_model: str = Field(..., description="设备型号")
    
    # 设备状态
    device_status: str = Field(..., description="设备状态: online|offline|maintenance")
    battery_level: int = Field(..., description="电池电量百分比", ge=0, le=100)
    storage_available_mb: float = Field(..., description="可用存储空间（MB）")
    memory_usage_mb: float = Field(..., description="内存使用量（MB）")
    
    # 网络状态
    network_type: str = Field(..., description="网络类型: wifi|4g|5g|ethernet")
    network_quality: NetworkQuality = Field(..., description="网络质量")
    signal_strength: int = Field(..., description="信号强度", ge=0, le=100)
    
    # 功能状态
    camera_available: bool = Field(default=True, description="摄像头是否可用")
    gps_available: bool = Field(default=True, description="GPS是否可用")
    nfc_available: bool = Field(default=False, description="NFC是否可用")
    bluetooth_available: bool = Field(default=True, description="蓝牙是否可用")
    
    # 应用状态
    app_running: bool = Field(default=True, description="应用是否运行中")
    last_activity_time: datetime = Field(..., description="最后活动时间")
    session_duration_minutes: int = Field(default=0, description="会话持续时间（分钟）")
    
    # 位置信息
    current_location: Optional[Dict[str, float]] = Field(None, description="当前位置（经纬度）")
    location_accuracy_meters: Optional[float] = Field(None, description="位置精度（米）")
    
    # 同步状态
    last_sync_time: Optional[datetime] = Field(None, description="最后同步时间")
    sync_pending: bool = Field(default=False, description="是否有待同步数据")
    
    # 错误信息
    error_count: int = Field(default=0, description="错误计数")
    last_error_message: Optional[str] = Field(None, description="最后错误消息")
    
    # 操作员信息
    current_operator: Optional[str] = Field(None, description="当前操作员")
    operator_login_time: Optional[datetime] = Field(None, description="操作员登录时间")
    
    # 配置信息
    configuration_version: str = Field(..., description="配置版本")
    auto_sync_enabled: bool = Field(default=True, description="是否启用自动同步")
    offline_mode_enabled: bool = Field(default=True, description="是否启用离线模式")
    
    status_timestamp: datetime = Field(default_factory=datetime.now, description="状态时间戳")


class MobilePhotoUploadDTO(BaseModel):
    """移动端照片上传DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    upload_id: str = Field(..., description="上传ID")
    device_id: str = Field(..., description="设备ID")
    
    # 照片信息
    photo_type: str = Field(..., description="照片类型: visitor_entry|incident|verification|checkin")
    photo_filename: str = Field(..., description="照片文件名")
    photo_size_kb: float = Field(..., description="照片大小（KB）")
    photo_format: str = Field(..., description="照片格式: jpg|png|webp")
    photo_quality: PhotoQuality = Field(..., description="照片质量")
    
    # 关联信息
    visitor_id: Optional[int] = Field(None, description="关联访客ID")
    verification_id: Optional[str] = Field(None, description="关联验证ID")
    incident_id: Optional[str] = Field(None, description="关联事件ID")
    
    # 拍摄信息
    capture_timestamp: datetime = Field(..., description="拍摄时间戳")
    capture_location: Optional[Dict[str, float]] = Field(None, description="拍摄位置")
    camera_settings: Dict[str, Any] = Field(default_factory=dict, description="相机设置")
    
    # 上传信息
    upload_timestamp: datetime = Field(default_factory=datetime.now, description="上传时间戳")
    upload_status: str = Field(default="pending", description="上传状态: pending|uploading|completed|failed")
    upload_progress: int = Field(default=0, description="上传进度百分比", ge=0, le=100)
    
    # 处理信息
    auto_enhancement: bool = Field(default=True, description="是否自动增强")
    face_detection_enabled: bool = Field(default=False, description="是否启用人脸检测")
    ocr_enabled: bool = Field(default=False, description="是否启用OCR识别")
    
    # 存储信息
    storage_path: Optional[str] = Field(None, description="存储路径")
    cdn_url: Optional[str] = Field(None, description="CDN访问URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    
    # 安全信息
    encryption_enabled: bool = Field(default=True, description="是否加密存储")
    access_level: str = Field(default="restricted", description="访问级别")
    retention_days: int = Field(default=90, description="保留天数")
    
    # 操作信息
    operator: str = Field(..., description="操作员ID")
    gate_id: Optional[str] = Field(None, description="门岗ID")
    
    # 错误信息
    error_message: Optional[str] = Field(None, description="错误信息")
    retry_count: int = Field(default=0, description="重试次数")
    
    remarks: Optional[str] = Field(None, description="备注信息") 