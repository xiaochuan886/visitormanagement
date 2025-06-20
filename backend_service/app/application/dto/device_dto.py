"""
设备管理数据传输对象
"""
from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class DeviceType(str, Enum):
    """设备类型枚举"""
    GATE_TERMINAL = "gate_terminal"
    RECEPTION_KIOSK = "reception_kiosk"
    MOBILE_TABLET = "mobile_tablet"
    ACCESS_CONTROL = "access_control"
    CAMERA_SYSTEM = "camera_system"
    PRINTER = "printer"
    ID_SCANNER = "id_scanner"
    FACE_RECOGNITION = "face_recognition"
    QR_SCANNER = "qr_scanner"
    INTERCOM = "intercom"
    BADGE_PRINTER = "badge_printer"


class DeviceStatus(str, Enum):
    """设备状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    DISABLED = "disabled"
    STANDBY = "standby"
    BUSY = "busy"


class ConnectionType(str, Enum):
    """连接类型枚举"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    USB = "usb"
    BLUETOOTH = "bluetooth"
    SERIAL = "serial"
    WIRELESS_4G = "wireless_4g"
    WIRELESS_5G = "wireless_5g"


class MaintenanceType(str, Enum):
    """维护类型枚举"""
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    UPGRADE = "upgrade"
    CALIBRATION = "calibration"
    CLEANING = "cleaning"


class DeviceCapability(str, Enum):
    """设备能力枚举"""
    QR_SCAN = "qr_scan"
    FACE_RECOGNITION = "face_recognition"
    ID_CARD_SCAN = "id_card_scan"
    PHOTO_CAPTURE = "photo_capture"
    AUDIO_RECORDING = "audio_recording"
    PRINTING = "printing"
    BADGE_DISPENSING = "badge_dispensing"
    ACCESS_CONTROL = "access_control"
    INTERCOM_COMMUNICATION = "intercom_communication"
    ENVIRONMENTAL_MONITORING = "environmental_monitoring"


class DeviceInfoDTO(BaseModel):
    """设备信息DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_type: DeviceType = Field(..., description="设备类型")
    
    # 基本信息
    manufacturer: str = Field(..., description="制造商")
    model: str = Field(..., description="设备型号")
    serial_number: str = Field(..., description="序列号")
    firmware_version: str = Field(..., description="固件版本")
    
    # 位置信息
    site_id: int = Field(..., description="所属站点ID")
    location_description: str = Field(..., description="位置描述")
    installation_date: date = Field(..., description="安装日期")
    
    # 状态信息
    status: DeviceStatus = Field(..., description="设备状态")
    last_seen: datetime = Field(default_factory=datetime.now, description="最后在线时间")
    uptime_hours: float = Field(default=0.0, description="运行时间（小时）")
    
    # 连接信息
    connection_type: ConnectionType = Field(..., description="连接类型")
    ip_address: Optional[str] = Field(None, description="IP地址")
    mac_address: Optional[str] = Field(None, description="MAC地址")
    
    # 能力信息
    capabilities: List[DeviceCapability] = Field(default_factory=list, description="设备能力")
    max_concurrent_users: int = Field(default=1, description="最大并发用户数")
    
    # 管理信息
    responsible_person: str = Field(..., description="责任人")
    maintenance_contact: str = Field(..., description="维护联系人")
    support_phone: Optional[str] = Field(None, description="技术支持电话")
    
    # 配置信息
    configuration: Dict[str, Any] = Field(default_factory=dict, description="设备配置")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="自定义设置")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    notes: Optional[str] = Field(None, description="备注信息")


class DeviceStatusDTO(BaseModel):
    """设备状态监控DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    status_timestamp: datetime = Field(default_factory=datetime.now, description="状态时间戳")
    
    # 运行状态
    operational_status: DeviceStatus = Field(..., description="运行状态")
    cpu_usage_percent: float = Field(..., description="CPU使用率", ge=0, le=100)
    memory_usage_percent: float = Field(..., description="内存使用率", ge=0, le=100)
    storage_usage_percent: float = Field(..., description="存储使用率", ge=0, le=100)
    
    # 网络状态
    network_status: str = Field(..., description="网络状态: connected|disconnected|unstable")
    network_latency_ms: Optional[float] = Field(None, description="网络延迟（毫秒）")
    bandwidth_utilization_percent: Optional[float] = Field(None, description="带宽利用率")
    
    # 硬件状态
    temperature_celsius: Optional[float] = Field(None, description="设备温度（摄氏度）")
    power_consumption_watts: Optional[float] = Field(None, description="功耗（瓦特）")
    battery_level_percent: Optional[int] = Field(None, description="电池电量", ge=0, le=100)
    
    # 服务状态
    active_sessions: int = Field(default=0, description="活跃会话数")
    pending_operations: int = Field(default=0, description="待处理操作数")
    queue_length: int = Field(default=0, description="队列长度")
    
    # 错误信息
    error_count: int = Field(default=0, description="错误计数")
    warning_count: int = Field(default=0, description="警告计数")
    last_error_message: Optional[str] = Field(None, description="最后错误消息")
    
    # 性能指标
    response_time_ms: float = Field(..., description="响应时间（毫秒）")
    throughput_per_minute: float = Field(..., description="每分钟处理量")
    success_rate_percent: float = Field(..., description="成功率", ge=0, le=100)
    
    # 外部依赖状态
    database_connection: bool = Field(default=True, description="数据库连接状态")
    cache_connection: bool = Field(default=True, description="缓存连接状态")
    external_api_status: Dict[str, bool] = Field(default_factory=dict, description="外部API状态")
    
    # 维护信息
    maintenance_required: bool = Field(default=False, description="是否需要维护")
    next_maintenance_date: Optional[date] = Field(None, description="下次维护日期")
    
    reported_by: str = Field(..., description="报告者")


class DeviceMaintenanceDTO(BaseModel):
    """设备维护记录DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    maintenance_id: str = Field(..., description="维护记录ID")
    device_id: str = Field(..., description="设备ID")
    
    # 维护基本信息
    maintenance_type: MaintenanceType = Field(..., description="维护类型")
    title: str = Field(..., description="维护标题")
    description: str = Field(..., description="维护描述")
    
    # 时间信息
    scheduled_date: date = Field(..., description="计划维护日期")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration_hours: Optional[float] = Field(None, description="持续时间（小时）")
    
    # 人员信息
    technician: str = Field(..., description="技术人员")
    supervisor: Optional[str] = Field(None, description="主管")
    requester: str = Field(..., description="申请人")
    
    # 维护内容
    tasks_performed: List[str] = Field(default_factory=list, description="执行的任务")
    parts_replaced: List[Dict[str, Any]] = Field(default_factory=list, description="更换的部件")
    tools_used: List[str] = Field(default_factory=list, description="使用的工具")
    
    # 成本信息
    labor_cost: Optional[float] = Field(None, description="人工成本")
    parts_cost: Optional[float] = Field(None, description="部件成本")
    total_cost: Optional[float] = Field(None, description="总成本")
    
    # 状态信息
    maintenance_status: str = Field(..., description="维护状态: planned|in_progress|completed|cancelled")
    completion_percentage: int = Field(default=0, description="完成百分比", ge=0, le=100)
    
    # 问题和解决方案
    issues_found: List[str] = Field(default_factory=list, description="发现的问题")
    solutions_applied: List[str] = Field(default_factory=list, description="应用的解决方案")
    
    # 测试和验证
    tests_performed: List[str] = Field(default_factory=list, description="执行的测试")
    test_results: Dict[str, Any] = Field(default_factory=dict, description="测试结果")
    quality_check_passed: bool = Field(default=False, description="质量检查是否通过")
    
    # 后续行动
    follow_up_required: bool = Field(default=False, description="是否需要后续行动")
    next_maintenance_recommended: Optional[date] = Field(None, description="建议下次维护日期")
    warranty_status: Optional[str] = Field(None, description="保修状态")
    
    # 文档和附件
    photos_taken: List[str] = Field(default_factory=list, description="拍摄的照片")
    documents_attached: List[str] = Field(default_factory=list, description="附加的文档")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    notes: Optional[str] = Field(None, description="备注")


class DeviceConfigurationDTO(BaseModel):
    """设备配置DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    configuration_id: str = Field(..., description="配置ID")
    
    # 配置基本信息
    configuration_name: str = Field(..., description="配置名称")
    configuration_version: str = Field(..., description="配置版本")
    environment: str = Field(..., description="环境: production|staging|development")
    
    # 网络配置
    network_settings: Dict[str, Any] = Field(default_factory=dict, description="网络设置")
    
    # 功能配置
    feature_flags: Dict[str, bool] = Field(default_factory=dict, description="功能开关")
    operation_modes: Dict[str, str] = Field(default_factory=dict, description="操作模式")
    
    # 安全配置
    security_settings: Dict[str, Any] = Field(default_factory=dict, description="安全设置")
    access_permissions: List[str] = Field(default_factory=list, description="访问权限")
    
    # 性能配置
    performance_settings: Dict[str, Any] = Field(default_factory=dict, description="性能设置")
    resource_limits: Dict[str, Union[int, float]] = Field(default_factory=dict, description="资源限制")
    
    # 界面配置
    ui_settings: Dict[str, Any] = Field(default_factory=dict, description="用户界面设置")
    display_options: Dict[str, Any] = Field(default_factory=dict, description="显示选项")
    
    # 集成配置
    api_endpoints: Dict[str, str] = Field(default_factory=dict, description="API端点")
    external_services: Dict[str, Any] = Field(default_factory=dict, description="外部服务配置")
    
    # 日志和监控配置
    logging_settings: Dict[str, Any] = Field(default_factory=dict, description="日志设置")
    monitoring_settings: Dict[str, Any] = Field(default_factory=dict, description="监控设置")
    
    # 备份和恢复配置
    backup_settings: Dict[str, Any] = Field(default_factory=dict, description="备份设置")
    recovery_settings: Dict[str, Any] = Field(default_factory=dict, description="恢复设置")
    
    # 配置管理
    configuration_source: str = Field(..., description="配置来源: manual|template|auto_generated")
    deployment_status: str = Field(..., description="部署状态: pending|deployed|failed|rollback")
    
    # 验证信息
    validation_status: str = Field(..., description="验证状态: pending|passed|failed")
    validation_errors: List[str] = Field(default_factory=list, description="验证错误")
    
    # 历史信息
    previous_version: Optional[str] = Field(None, description="上一版本")
    change_reason: str = Field(..., description="变更原因")
    rollback_available: bool = Field(default=True, description="是否可回滚")
    
    # 生效时间
    effective_from: datetime = Field(default_factory=datetime.now, description="生效开始时间")
    effective_until: Optional[datetime] = Field(None, description="生效结束时间")
    
    # 元数据
    created_by: str = Field(..., description="创建者")
    approved_by: Optional[str] = Field(None, description="审批者")
    deployed_by: Optional[str] = Field(None, description="部署者")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    comments: Optional[str] = Field(None, description="配置说明")


class DeviceAlertDTO(BaseModel):
    """设备告警DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    alert_id: str = Field(..., description="告警ID")
    device_id: str = Field(..., description="设备ID")
    
    # 告警基本信息
    alert_type: str = Field(..., description="告警类型: error|warning|info|critical")
    alert_source: str = Field(..., description="告警来源")
    alert_code: str = Field(..., description="告警代码")
    title: str = Field(..., description="告警标题")
    message: str = Field(..., description="告警消息")
    
    # 严重程度
    severity: str = Field(..., description="严重程度: low|medium|high|critical")
    priority: int = Field(..., description="优先级", ge=1, le=10)
    urgency: str = Field(..., description="紧急程度: low|medium|high")
    
    # 时间信息
    triggered_at: datetime = Field(default_factory=datetime.now, description="触发时间")
    first_occurrence: datetime = Field(default_factory=datetime.now, description="首次发生时间")
    last_occurrence: datetime = Field(default_factory=datetime.now, description="最后发生时间")
    occurrence_count: int = Field(default=1, description="发生次数")
    
    # 状态信息
    alert_status: str = Field(..., description="告警状态: active|acknowledged|resolved|suppressed")
    acknowledgment_time: Optional[datetime] = Field(None, description="确认时间")
    resolution_time: Optional[datetime] = Field(None, description="解决时间")
    
    # 影响范围
    affected_components: List[str] = Field(default_factory=list, description="受影响组件")
    impact_level: str = Field(..., description="影响级别: none|minor|major|severe")
    business_impact: Optional[str] = Field(None, description="业务影响描述")
    
    # 根本原因
    root_cause: Optional[str] = Field(None, description="根本原因")
    contributing_factors: List[str] = Field(default_factory=list, description="促成因素")
    
    # 解决方案
    recommended_actions: List[str] = Field(default_factory=list, description="建议行动")
    resolution_steps: List[str] = Field(default_factory=list, description="解决步骤")
    workaround: Optional[str] = Field(None, description="临时解决方案")
    
    # 通知信息
    notification_sent: bool = Field(default=False, description="是否已发送通知")
    notification_recipients: List[str] = Field(default_factory=list, description="通知接收者")
    escalation_level: int = Field(default=0, description="升级级别")
    
    # 关联信息
    related_alerts: List[str] = Field(default_factory=list, description="相关告警")
    maintenance_ticket: Optional[str] = Field(None, description="维护工单")
    incident_id: Optional[str] = Field(None, description="事件ID")
    
    # 监控数据
    metric_values: Dict[str, Any] = Field(default_factory=dict, description="度量值")
    threshold_values: Dict[str, Any] = Field(default_factory=dict, description="阈值")
    
    # 处理人员
    assigned_to: Optional[str] = Field(None, description="分配给")
    acknowledged_by: Optional[str] = Field(None, description="确认人")
    resolved_by: Optional[str] = Field(None, description="解决人")
    
    # 自动化信息
    auto_resolution_attempted: bool = Field(default=False, description="是否尝试自动解决")
    auto_resolution_success: bool = Field(default=False, description="自动解决是否成功")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    additional_data: Dict[str, Any] = Field(default_factory=dict, description="附加数据")
    comments: Optional[str] = Field(None, description="备注")


class DeviceUsageStatisticsDTO(BaseModel):
    """设备使用统计DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    device_id: str = Field(..., description="设备ID")
    statistics_date: date = Field(..., description="统计日期")
    report_period: str = Field(..., description="报告周期: daily|weekly|monthly|yearly")
    
    # 基本使用统计
    total_usage_hours: float = Field(..., description="总使用小时数")
    active_time_hours: float = Field(..., description="活跃时间小时数")
    idle_time_hours: float = Field(..., description="空闲时间小时数")
    downtime_hours: float = Field(..., description="停机时间小时数")
    
    # 操作统计
    total_operations: int = Field(..., description="总操作次数")
    successful_operations: int = Field(..., description="成功操作次数")
    failed_operations: int = Field(..., description="失败操作次数")
    average_operation_time_seconds: float = Field(..., description="平均操作时间（秒）")
    
    # 用户统计
    unique_users: int = Field(..., description="唯一用户数")
    total_sessions: int = Field(..., description="总会话数")
    average_session_duration_minutes: float = Field(..., description="平均会话时长（分钟）")
    
    # 性能统计
    average_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    peak_response_time_ms: float = Field(..., description="峰值响应时间（毫秒）")
    throughput_per_hour: float = Field(..., description="每小时吞吐量")
    
    # 错误统计
    error_count: int = Field(..., description="错误总数")
    warning_count: int = Field(..., description="警告总数")
    critical_error_count: int = Field(..., description="严重错误数")
    
    # 可用性统计
    uptime_percentage: float = Field(..., description="正常运行时间百分比", ge=0, le=100)
    availability_percentage: float = Field(..., description="可用性百分比", ge=0, le=100)
    reliability_score: float = Field(..., description="可靠性评分", ge=0, le=10)
    
    # 资源利用率
    cpu_utilization_avg: float = Field(..., description="平均CPU利用率", ge=0, le=100)
    memory_utilization_avg: float = Field(..., description="平均内存利用率", ge=0, le=100)
    storage_utilization_avg: float = Field(..., description="平均存储利用率", ge=0, le=100)
    network_utilization_avg: float = Field(..., description="平均网络利用率", ge=0, le=100)
    
    # 功能使用统计
    feature_usage: Dict[str, int] = Field(default_factory=dict, description="功能使用统计")
    most_used_features: List[str] = Field(default_factory=list, description="最常用功能")
    
    # 峰值信息
    peak_usage_time: Optional[time] = Field(None, description="峰值使用时间")
    peak_concurrent_users: int = Field(..., description="峰值并发用户数")
    busiest_hour: int = Field(..., description="最繁忙小时", ge=0, le=23)
    
    # 趋势信息
    usage_trend: str = Field(..., description="使用趋势: increasing|stable|decreasing")
    performance_trend: str = Field(..., description="性能趋势: improving|stable|degrading")
    
    # 维护影响
    maintenance_downtime_hours: float = Field(..., description="维护停机时间（小时）")
    unplanned_downtime_hours: float = Field(..., description="计划外停机时间（小时）")
    
    # 成本效益
    operational_cost: Optional[float] = Field(None, description="运营成本")
    cost_per_operation: Optional[float] = Field(None, description="每次操作成本")
    
    # 比较基准
    compared_to_previous_period: Dict[str, float] = Field(default_factory=dict, description="与上期比较")
    industry_benchmark_comparison: Dict[str, float] = Field(default_factory=dict, description="行业基准比较")
    
    # 元数据
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    generated_by: str = Field(..., description="生成者")
    
    notes: Optional[str] = Field(None, description="统计说明")


# 设备操作相关DTO
class DeviceOperationRequestDTO(BaseModel):
    """设备操作请求DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    operation_id: str = Field(..., description="操作ID")
    device_id: str = Field(..., description="设备ID")
    operation_type: str = Field(..., description="操作类型: restart|shutdown|configure|update")
    
    # 操作参数
    operation_parameters: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
    priority: int = Field(default=5, description="优先级", ge=1, le=10)
    
    # 调度信息
    scheduled_time: Optional[datetime] = Field(None, description="计划执行时间")
    timeout_seconds: int = Field(default=300, description="超时时间（秒）")
    
    # 安全检查
    require_confirmation: bool = Field(default=True, description="是否需要确认")
    bypass_safety_checks: bool = Field(default=False, description="是否绕过安全检查")
    
    # 元数据
    requested_by: str = Field(..., description="请求人")
    reason: str = Field(..., description="操作原因")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class DeviceOperationResponseDTO(BaseModel):
    """设备操作响应DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    operation_id: str = Field(..., description="操作ID")
    device_id: str = Field(..., description="设备ID")
    
    # 执行状态
    status: str = Field(..., description="执行状态: pending|running|completed|failed|cancelled")
    result_code: int = Field(..., description="结果代码")
    result_message: str = Field(..., description="结果消息")
    
    # 执行时间
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    duration_seconds: Optional[float] = Field(None, description="执行时长（秒）")
    
    # 执行结果
    output_data: Dict[str, Any] = Field(default_factory=dict, description="输出数据")
    error_details: Optional[str] = Field(None, description="错误详情")
    
    # 设备状态变化
    device_status_before: Optional[DeviceStatus] = Field(None, description="操作前设备状态")
    device_status_after: Optional[DeviceStatus] = Field(None, description="操作后设备状态")
    
    # 元数据
    executed_by: Optional[str] = Field(None, description="执行人")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class DeviceBatchOperationDTO(BaseModel):
    """设备批量操作DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    batch_id: str = Field(..., description="批次ID")
    operation_type: str = Field(..., description="操作类型")
    
    # 目标设备
    device_ids: List[str] = Field(..., description="设备ID列表")
    device_filter: Optional[Dict[str, Any]] = Field(None, description="设备筛选条件")
    
    # 批量参数
    batch_size: int = Field(default=10, description="批次大小")
    parallel_execution: bool = Field(default=False, description="是否并行执行")
    continue_on_error: bool = Field(default=True, description="出错时是否继续")
    
    # 执行统计
    total_devices: int = Field(..., description="总设备数")
    successful_count: int = Field(default=0, description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    pending_count: int = Field(default=0, description="待处理数量")
    
    # 元数据
    created_by: str = Field(..., description="创建者")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
