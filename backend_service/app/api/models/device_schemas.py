"""
设备管理系统 Schema 定义
包含设备注册、状态监控、配置管理等相关数据传输对象
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

from app.api.models.base_response import BaseResponseModel


# 枚举定义
class DeviceType(str, Enum):
    """设备类型枚举"""
    GATE_TERMINAL = "gate_terminal"
    RECEPTION_KIOSK = "reception_kiosk"
    MOBILE_TABLET = "mobile_tablet"
    ACCESS_CONTROL = "access_control"
    CAMERA = "camera"
    PRINTER = "printer"
    SCANNER = "scanner"
    DISPLAY = "display"
    SENSOR = "sensor"


class DeviceStatus(str, Enum):
    """设备状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"


class AlertLevel(str, Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# 设备注册 Schema
class DeviceRegistrationRequestSchema(BaseModel):
    """设备注册请求Schema"""
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_type: DeviceType = Field(..., description="设备类型")
    location: str = Field(..., description="设备位置")
    ip_address: Optional[str] = Field(None, description="IP地址")
    mac_address: Optional[str] = Field(None, description="MAC地址")
    firmware_version: Optional[str] = Field(None, description="固件版本")
    hardware_info: Optional[Dict[str, str]] = Field(None, description="硬件信息")
    capabilities: List[str] = Field(default=[], description="设备能力")
    configuration: Optional[Dict[str, Any]] = Field(None, description="设备配置")


class DeviceRegistrationResponseSchema(BaseResponseModel):
    """设备注册响应Schema"""
    device_id: str = Field(..., description="设备ID")
    registration_time: datetime = Field(..., description="注册时间")
    device_status: DeviceStatus = Field(..., description="设备状态")
    assigned_config: Dict[str, Any] = Field(..., description="分配的配置")
    security_token: Optional[str] = Field(None, description="安全令牌")
    heartbeat_interval: int = Field(..., description="心跳间隔(秒)")


# 设备状态更新 Schema
class DeviceStatusUpdateRequestSchema(BaseModel):
    """设备状态更新请求Schema"""
    device_id: str = Field(..., description="设备ID")
    status: DeviceStatus = Field(..., description="设备状态")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率", ge=0, le=100)
    memory_usage: Optional[float] = Field(None, description="内存使用率", ge=0, le=100)
    disk_usage: Optional[float] = Field(None, description="磁盘使用率", ge=0, le=100)
    temperature: Optional[float] = Field(None, description="温度(摄氏度)")
    network_latency: Optional[float] = Field(None, description="网络延迟(毫秒)")
    error_messages: Optional[List[str]] = Field(None, description="错误信息")
    performance_metrics: Optional[Dict[str, float]] = Field(None, description="性能指标")


class DeviceStatusUpdateResponseSchema(BaseResponseModel):
    """设备状态更新响应Schema"""
    device_id: str = Field(..., description="设备ID")
    status_updated: bool = Field(..., description="状态是否更新")
    update_time: datetime = Field(..., description="更新时间")
    health_score: float = Field(..., description="健康评分", ge=0, le=100)
    recommendations: List[str] = Field(default=[], description="建议")
    alerts: List[Dict[str, Any]] = Field(default=[], description="告警信息")


# 设备配置更新 Schema
class DeviceConfigUpdateRequestSchema(BaseModel):
    """设备配置更新请求Schema"""
    device_id: str = Field(..., description="设备ID")
    configuration: Dict[str, Any] = Field(..., description="配置参数")
    apply_immediately: bool = Field(True, description="是否立即应用")
    backup_current: bool = Field(True, description="是否备份当前配置")


class DeviceConfigUpdateResponseSchema(BaseResponseModel):
    """设备配置更新响应Schema"""
    device_id: str = Field(..., description="设备ID")
    config_applied: bool = Field(..., description="配置是否应用")
    update_time: datetime = Field(..., description="更新时间")
    backup_id: Optional[str] = Field(None, description="备份ID")
    restart_required: bool = Field(..., description="是否需要重启")


# 设备维护 Schema
class DeviceMaintenanceRequestSchema(BaseModel):
    """设备维护请求Schema"""
    device_id: str = Field(..., description="设备ID")
    maintenance_type: str = Field(..., description="维护类型")
    scheduled_time: Optional[datetime] = Field(None, description="计划时间")
    description: str = Field(..., description="维护描述")
    estimated_duration: Optional[int] = Field(None, description="预计时长(分钟)")
    technician: Optional[str] = Field(None, description="技术员")


class DeviceMaintenanceResponseSchema(BaseResponseModel):
    """设备维护响应Schema"""
    maintenance_id: str = Field(..., description="维护ID")
    device_id: str = Field(..., description="设备ID")
    maintenance_status: str = Field(..., description="维护状态")
    scheduled_time: datetime = Field(..., description="计划时间")
    maintenance_window: Dict[str, datetime] = Field(..., description="维护窗口")


# 设备列表查询 Schema
class DeviceListRequestSchema(BaseModel):
    """设备列表查询请求Schema"""
    device_type: Optional[DeviceType] = Field(None, description="设备类型筛选")
    status: Optional[DeviceStatus] = Field(None, description="状态筛选")
    location: Optional[str] = Field(None, description="位置筛选")
    search_keyword: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, description="页码", ge=1)
    size: int = Field(20, description="页面大小", ge=1, le=100)


class DeviceItemSchema(BaseModel):
    """设备条目Schema"""
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_type: str = Field(..., description="设备类型")
    location: str = Field(..., description="位置")
    status: str = Field(..., description="状态")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳")
    health_score: Optional[float] = Field(None, description="健康评分")
    uptime: Optional[int] = Field(None, description="运行时间(小时)")


class DeviceListResponseSchema(BaseResponseModel):
    """设备列表响应Schema"""
    devices: List[DeviceItemSchema] = Field(..., description="设备列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="页面大小")
    summary: Dict[str, Any] = Field(..., description="统计摘要")


# 设备详情 Schema
class DeviceDetailResponseSchema(BaseResponseModel):
    """设备详情响应Schema"""
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_type: str = Field(..., description="设备类型")
    location: str = Field(..., description="位置")
    status: str = Field(..., description="状态")
    registration_time: datetime = Field(..., description="注册时间")
    last_update: datetime = Field(..., description="最后更新")
    hardware_info: Dict[str, str] = Field(..., description="硬件信息")
    capabilities: List[str] = Field(..., description="设备能力")
    current_config: Dict[str, Any] = Field(..., description="当前配置")
    performance_stats: Dict[str, float] = Field(..., description="性能统计")
    recent_alerts: List[Dict[str, Any]] = Field(..., description="最近告警")


# 设备使用统计 Schema
class DeviceUsageStatsRequestSchema(BaseModel):
    """设备使用统计请求Schema"""
    device_id: str = Field(..., description="设备ID")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    group_by: str = Field("day", description="分组方式")


class DeviceUsageStatsResponseSchema(BaseResponseModel):
    """设备使用统计响应Schema"""
    device_id: str = Field(..., description="设备ID")
    total_usage_time: int = Field(..., description="总使用时间(小时)")
    average_daily_usage: float = Field(..., description="日均使用时间(小时)")
    peak_usage_hours: List[str] = Field(..., description="使用高峰时段")
    downtime_events: int = Field(..., description="停机事件数")
    maintenance_count: int = Field(..., description="维护次数")
    utilization_rate: float = Field(..., description="使用率(%)")
    usage_trend: Dict[str, float] = Field(..., description="使用趋势")


# 设备告警配置 Schema
class DeviceAlertConfigRequestSchema(BaseModel):
    """设备告警配置请求Schema"""
    device_id: str = Field(..., description="设备ID")
    alert_rules: List[Dict[str, Any]] = Field(..., description="告警规则")
    notification_channels: List[str] = Field(..., description="通知渠道")
    escalation_policy: Optional[Dict[str, Any]] = Field(None, description="升级策略")


class DeviceAlertConfigResponseSchema(BaseResponseModel):
    """设备告警配置响应Schema"""
    device_id: str = Field(..., description="设备ID")
    config_updated: bool = Field(..., description="配置是否更新")
    active_rules: int = Field(..., description="活跃规则数")
    update_time: datetime = Field(..., description="更新时间")


# 设备监控仪表板 Schema
class DeviceMonitoringRequestSchema(BaseModel):
    """设备监控仪表板请求Schema"""
    time_range: str = Field("1h", description="时间范围")
    device_types: Optional[List[DeviceType]] = Field(None, description="设备类型筛选")


class DeviceMonitoringResponseSchema(BaseResponseModel):
    """设备监控仪表板响应Schema"""
    total_devices: int = Field(..., description="设备总数")
    online_devices: int = Field(..., description="在线设备数")
    offline_devices: int = Field(..., description="离线设备数")
    error_devices: int = Field(..., description="错误设备数")
    availability_rate: float = Field(..., description="可用率(%)")
    active_alerts: int = Field(..., description="活跃告警数")
    device_type_stats: Dict[str, int] = Field(..., description="设备类型统计")
    recent_events: List[Dict[str, Any]] = Field(..., description="最近事件")
    performance_overview: Dict[str, float] = Field(..., description="性能概览") 