"""
访客管理系统 - 领域枚举类包初始化

导出配置引擎和空间管理相关的所有枚举类
"""

from .config_enums import (
    FormType,
    FieldType,
    WorkflowType,
    WorkflowStatus,
    StepType,
    ApprovalType,
    BusinessRuleCategory,
    RuleExecutionResult,
    ConfigurationStatus,
    ValidationSeverity,
    CacheStrategy,
    EventType
)

from .spatial_enums import (
    SpatialType,
    AccessControlType,
    DeviceType,
    LocationDataType,
    SpatialCapabilityType,
    OperatingStatus,
    AccessLevelType,
    TimeRestrictionType,
    PathfindingAlgorithm,
    SpatialRelationType,
    EnvironmentalParameter,
    CapacityType,
    SecurityLevel,
    MaintenanceType
)

__all__ = [
    # 配置枚举
    "FormType",
    "FieldType", 
    "WorkflowType",
    "WorkflowStatus",
    "StepType",
    "ApprovalType",
    "BusinessRuleCategory",
    "RuleExecutionResult",
    "ConfigurationStatus",
    "ValidationSeverity",
    "CacheStrategy",
    "EventType",
    # 空间枚举
    "SpatialType",
    "AccessControlType",
    "DeviceType",
    "LocationDataType",
    "SpatialCapabilityType",
    "OperatingStatus",
    "AccessLevelType",
    "TimeRestrictionType",
    "PathfindingAlgorithm",
    "SpatialRelationType",
    "EnvironmentalParameter",
    "CapacityType",
    "SecurityLevel",
    "MaintenanceType"
] 