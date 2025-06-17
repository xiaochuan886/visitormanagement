"""
空间配置相关DTO定义
定义空间配置系统中的数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.domain.enums.spatial_enums import (
    SpatialType, AccessControlType, DeviceType, LocationDataType,
    OperatingStatus, AccessLevelType, TimeRestrictionType, SecurityLevel
)


class SpatialLevelConfigurationDTO(BaseModel):
    """空间层级配置DTO"""
    level_name: str = Field(..., description="层级名称", min_length=1, max_length=50)
    spatial_type: SpatialType = Field(..., description="空间类型")
    level_order: int = Field(..., description="层级顺序", ge=0)
    is_required: bool = Field(True, description="是否必需层级")
    max_children: Optional[int] = Field(None, description="最大子层级数量", ge=0)
    naming_pattern: Optional[str] = Field(None, description="命名模式")
    default_properties: Optional[Dict[str, Any]] = Field(None, description="默认属性")

    @validator('naming_pattern')
    def validate_naming_pattern(cls, v):
        """验证命名模式"""
        if v and '{' not in v:
            raise ValueError('命名模式应包含变量占位符，如 {building}-{floor}')
        return v


class SpatialConfigurationCreateDTO(BaseModel):
    """空间配置创建DTO"""
    config_name: str = Field(..., description="配置名称", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="配置描述")
    spatial_levels: List[SpatialLevelConfigurationDTO] = Field(..., description="空间层级配置", min_items=1)
    default_access_control: Dict[str, Any] = Field(..., description="默认访问控制规则")
    device_integration_config: Optional[Dict[str, Any]] = Field(None, description="设备集成配置")
    pathfinding_enabled: bool = Field(False, description="是否启用路径规划")
    capacity_management_enabled: bool = Field(False, description="是否启用容量管理")
    emergency_management_enabled: bool = Field(False, description="是否启用应急管理")
    
    @validator('spatial_levels')
    def validate_spatial_levels(cls, v):
        """验证空间层级配置"""
        if not v:
            raise ValueError('至少需要配置一个空间层级')
        
        # 检查层级名称重复
        level_names = [level.level_name for level in v]
        if len(level_names) != len(set(level_names)):
            raise ValueError('空间层级名称不能重复')
        
        # 检查层级顺序重复
        level_orders = [level.level_order for level in v]
        if len(level_orders) != len(set(level_orders)):
            raise ValueError('空间层级顺序不能重复')
        
        return v


class SpatialConfigurationUpdateDTO(BaseModel):
    """空间配置更新DTO"""
    config_name: Optional[str] = Field(None, description="配置名称", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="配置描述")
    spatial_levels: Optional[List[SpatialLevelConfigurationDTO]] = Field(None, description="空间层级配置")
    default_access_control: Optional[Dict[str, Any]] = Field(None, description="默认访问控制规则")
    device_integration_config: Optional[Dict[str, Any]] = Field(None, description="设备集成配置")
    pathfinding_enabled: Optional[bool] = Field(None, description="是否启用路径规划")
    capacity_management_enabled: Optional[bool] = Field(None, description="是否启用容量管理")
    emergency_management_enabled: Optional[bool] = Field(None, description="是否启用应急管理")
    is_active: Optional[bool] = Field(None, description="是否激活")


class SpatialEntityCreateDTO(BaseModel):
    """空间实体创建DTO"""
    spatial_config_id: UUID = Field(..., description="空间配置ID")
    entity_code: str = Field(..., description="实体编码", min_length=1, max_length=50)
    entity_name: str = Field(..., description="实体名称", min_length=1, max_length=100)
    spatial_type: SpatialType = Field(..., description="空间类型")
    level: int = Field(..., description="层级级别", ge=0)
    parent_id: Optional[UUID] = Field(None, description="父级实体ID")
    description: Optional[str] = Field(None, description="实体描述")
    properties: Optional[Dict[str, Any]] = Field(None, description="实体属性")
    location_data: Optional[Dict[str, Any]] = Field(None, description="位置数据")
    capacity_config: Optional[Dict[str, Any]] = Field(None, description="容量配置")
    access_control_config: Optional[Dict[str, Any]] = Field(None, description="访问控制配置")
    device_bindings: Optional[List[str]] = Field(None, description="设备绑定列表")
    operating_status: OperatingStatus = Field(OperatingStatus.OPERATIONAL, description="运营状态")

    @validator('entity_code')
    def validate_entity_code(cls, v):
        """验证实体编码格式"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('实体编码只能包含字母、数字、横线和下划线')
        return v


class SpatialEntityUpdateDTO(BaseModel):
    """空间实体更新DTO"""
    entity_name: Optional[str] = Field(None, description="实体名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="实体描述")
    properties: Optional[Dict[str, Any]] = Field(None, description="实体属性")
    location_data: Optional[Dict[str, Any]] = Field(None, description="位置数据")
    capacity_config: Optional[Dict[str, Any]] = Field(None, description="容量配置")
    access_control_config: Optional[Dict[str, Any]] = Field(None, description="访问控制配置")
    device_bindings: Optional[List[str]] = Field(None, description="设备绑定列表")
    operating_status: Optional[OperatingStatus] = Field(None, description="运营状态")
    parent_id: Optional[UUID] = Field(None, description="父级实体ID")


class SpatialEntityResponseDTO(BaseModel):
    """空间实体响应DTO"""
    id: UUID = Field(..., description="实体ID")
    spatial_config_id: UUID = Field(..., description="空间配置ID")
    entity_code: str = Field(..., description="实体编码")
    entity_name: str = Field(..., description="实体名称")
    spatial_type: str = Field(..., description="空间类型")
    level: int = Field(..., description="层级级别")
    parent_id: Optional[UUID] = Field(None, description="父级实体ID")
    hierarchy_path: str = Field(..., description="层级路径")
    description: Optional[str] = Field(None, description="实体描述")
    properties: Optional[Dict[str, Any]] = Field(None, description="实体属性")
    location_data: Optional[Dict[str, Any]] = Field(None, description="位置数据")
    capacity_config: Optional[Dict[str, Any]] = Field(None, description="容量配置")
    access_control_config: Optional[Dict[str, Any]] = Field(None, description="访问控制配置")
    device_bindings: Optional[List[str]] = Field(None, description="设备绑定列表")
    operating_status: str = Field(..., description="运营状态")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")

    class Config:
        from_attributes = True


class SpatialConfigurationResponseDTO(BaseModel):
    """空间配置响应DTO"""
    id: UUID = Field(..., description="配置ID")
    config_name: str = Field(..., description="配置名称")
    config_version: int = Field(..., description="配置版本")
    description: Optional[str] = Field(None, description="配置描述")
    spatial_levels: List[Dict[str, Any]] = Field(..., description="空间层级配置")
    default_access_control: Dict[str, Any] = Field(..., description="默认访问控制规则")
    device_integration_config: Optional[Dict[str, Any]] = Field(None, description="设备集成配置")
    pathfinding_enabled: bool = Field(..., description="是否启用路径规划")
    capacity_management_enabled: bool = Field(..., description="是否启用容量管理")
    emergency_management_enabled: bool = Field(..., description="是否启用应急管理")
    is_active: bool = Field(..., description="是否激活")
    entity_count: int = Field(..., description="实体数量")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")

    class Config:
        from_attributes = True


class SpatialHierarchyDTO(BaseModel):
    """空间层级结构DTO"""
    entity_id: UUID = Field(..., description="实体ID")
    entity_code: str = Field(..., description="实体编码")
    entity_name: str = Field(..., description="实体名称")
    spatial_type: str = Field(..., description="空间类型")
    level: int = Field(..., description="层级级别")
    children: List['SpatialHierarchyDTO'] = Field([], description="子级实体列表")
    has_access_control: bool = Field(False, description="是否有访问控制")
    operating_status: str = Field(..., description="运营状态")

    class Config:
        from_attributes = True


class SpatialAccessControlDTO(BaseModel):
    """空间访问控制DTO"""
    entity_id: UUID = Field(..., description="空间实体ID")
    access_control_type: AccessControlType = Field(..., description="访问控制类型")
    access_level: AccessLevelType = Field(..., description="访问级别")
    time_restrictions: Optional[List[Dict[str, Any]]] = Field(None, description="时间限制")
    allowed_user_groups: Optional[List[str]] = Field(None, description="允许的用户组")
    allowed_roles: Optional[List[str]] = Field(None, description="允许的角色")
    security_requirements: Optional[Dict[str, Any]] = Field(None, description="安全要求")
    escort_required: bool = Field(False, description="是否需要陪同")
    approval_required: bool = Field(False, description="是否需要审批")


class SpatialDeviceBindingDTO(BaseModel):
    """空间设备绑定DTO"""
    entity_id: UUID = Field(..., description="空间实体ID")
    device_id: str = Field(..., description="设备ID")
    device_type: DeviceType = Field(..., description="设备类型")
    device_name: str = Field(..., description="设备名称")
    connection_config: Dict[str, Any] = Field(..., description="连接配置")
    control_permissions: List[str] = Field(..., description="控制权限")
    monitoring_enabled: bool = Field(True, description="是否启用监控")
    alert_enabled: bool = Field(True, description="是否启用告警")


class SpatialQueryDTO(BaseModel):
    """空间查询DTO"""
    spatial_config_id: Optional[UUID] = Field(None, description="空间配置ID")
    spatial_type: Optional[SpatialType] = Field(None, description="空间类型")
    parent_id: Optional[UUID] = Field(None, description="父级实体ID")
    level: Optional[int] = Field(None, description="层级级别", ge=0)
    entity_name: Optional[str] = Field(None, description="实体名称（模糊搜索）")
    operating_status: Optional[OperatingStatus] = Field(None, description="运营状态")
    has_access_control: Optional[bool] = Field(None, description="是否有访问控制")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class SpatialListResponseDTO(BaseModel):
    """空间列表响应DTO"""
    items: List[SpatialEntityResponseDTO] = Field(..., description="实体列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数")


class SpatialPathfindingRequestDTO(BaseModel):
    """空间路径规划请求DTO"""
    start_entity_id: UUID = Field(..., description="起始实体ID")
    end_entity_id: UUID = Field(..., description="目标实体ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    accessibility_requirements: Optional[List[str]] = Field(None, description="无障碍要求")
    avoid_restricted_areas: bool = Field(True, description="是否避开受限区域")
    preferred_route_type: str = Field("shortest", description="首选路径类型")


class SpatialPathfindingResponseDTO(BaseModel):
    """空间路径规划响应DTO"""
    route_id: UUID = Field(..., description="路径ID")
    waypoints: List[Dict[str, Any]] = Field(..., description="路径点列表")
    total_distance: float = Field(..., description="总距离（米）")
    estimated_time: int = Field(..., description="预计时间（秒）")
    route_instructions: List[str] = Field(..., description="路径指引")
    accessibility_compatible: bool = Field(..., description="是否符合无障碍要求")
    security_checkpoints: List[str] = Field([], description="安全检查点")


class SpatialCapacityStatusDTO(BaseModel):
    """空间容量状态DTO"""
    entity_id: UUID = Field(..., description="实体ID")
    capacity_type: str = Field(..., description="容量类型")
    max_capacity: int = Field(..., description="最大容量")
    current_occupancy: int = Field(..., description="当前占用")
    available_capacity: int = Field(..., description="可用容量")
    utilization_rate: float = Field(..., description="利用率")
    last_updated: datetime = Field(..., description="最后更新时间")


class SpatialEnvironmentalDataDTO(BaseModel):
    """空间环境数据DTO"""
    entity_id: UUID = Field(..., description="实体ID")
    temperature: Optional[float] = Field(None, description="温度（摄氏度）")
    humidity: Optional[float] = Field(None, description="湿度（%）")
    air_quality_index: Optional[int] = Field(None, description="空气质量指数")
    noise_level: Optional[float] = Field(None, description="噪音等级（分贝）")
    lighting_level: Optional[float] = Field(None, description="照明等级（勒克斯）")
    co2_level: Optional[float] = Field(None, description="二氧化碳浓度（ppm）")
    occupancy_count: Optional[int] = Field(None, description="在场人数")
    data_timestamp: datetime = Field(..., description="数据时间戳")


class SpatialAnalyticsDTO(BaseModel):
    """空间分析DTO"""
    entity_id: UUID = Field(..., description="实体ID")
    time_range: str = Field(..., description="时间范围")
    average_occupancy: float = Field(..., description="平均占用率")
    peak_occupancy: float = Field(..., description="峰值占用率")
    peak_time: str = Field(..., description="峰值时间")
    total_visits: int = Field(..., description="总访问次数")
    unique_visitors: int = Field(..., description="独立访客数")
    average_visit_duration: int = Field(..., description="平均访问时长（分钟）")
    environmental_trends: Dict[str, Any] = Field(..., description="环境趋势数据")


class SpatialConfigurationExportDTO(BaseModel):
    """空间配置导出DTO"""
    export_format: str = Field("json", description="导出格式")
    include_entities: bool = Field(True, description="是否包含实体数据")
    include_access_control: bool = Field(True, description="是否包含访问控制")
    include_device_bindings: bool = Field(True, description="是否包含设备绑定")
    include_analytics: bool = Field(False, description="是否包含分析数据")
    compress_output: bool = Field(False, description="是否压缩输出")


class SpatialValidationResultDTO(BaseModel):
    """空间配置验证结果DTO"""
    is_valid: bool = Field(..., description="是否验证通过")
    errors: List[Dict[str, Any]] = Field(..., description="错误信息列表")
    warnings: List[Dict[str, Any]] = Field(..., description="警告信息列表")
    hierarchy_errors: List[str] = Field(..., description="层级结构错误")
    access_control_errors: List[str] = Field(..., description="访问控制错误")
    device_binding_errors: List[str] = Field(..., description="设备绑定错误")
    validation_duration_ms: int = Field(..., description="验证耗时（毫秒）")


# 更新模型引用（避免循环引用）
SpatialHierarchyDTO.model_rebuild() 