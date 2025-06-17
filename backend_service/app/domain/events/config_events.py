"""
配置引擎相关领域事件定义
定义配置系统中的各种领域事件
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: UUID
    occurred_at: datetime
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_version: int
    tenant_id: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = uuid4()
        if not self.occurred_at:
            self.occurred_at = datetime.utcnow()
        if not self.metadata:
            self.metadata = {}


# ===== 表单配置事件 =====

@dataclass
class FormConfigurationCreated(DomainEvent):
    """表单配置创建事件"""
    form_type: str
    form_name: str
    field_count: int
    has_validation_rules: bool
    has_conditional_logic: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormConfigurationCreated"
        self.event_version = 1


@dataclass
class FormConfigurationUpdated(DomainEvent):
    """表单配置更新事件"""
    form_type: str
    form_name: str
    previous_version: int
    new_version: int
    changes: Dict[str, Any]
    field_changes: List[Dict[str, Any]]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormConfigurationUpdated"
        self.event_version = 1


@dataclass
class FormConfigurationActivated(DomainEvent):
    """表单配置激活事件"""
    form_type: str
    form_name: str
    previous_active_config_id: Optional[str]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormConfigurationActivated"
        self.event_version = 1


@dataclass
class FormConfigurationDeactivated(DomainEvent):
    """表单配置停用事件"""
    form_type: str
    form_name: str
    reason: str
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormConfigurationDeactivated"
        self.event_version = 1


@dataclass
class FormFieldAdded(DomainEvent):
    """表单字段添加事件"""
    form_config_id: str
    field_key: str
    field_type: str
    field_order: int
    is_required: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormFieldAdded"
        self.event_version = 1


@dataclass
class FormFieldRemoved(DomainEvent):
    """表单字段移除事件"""
    form_config_id: str
    field_key: str
    field_type: str
    reason: str
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "FormConfiguration"
        self.event_type = "FormFieldRemoved"
        self.event_version = 1


# ===== 工作流事件 =====

@dataclass
class WorkflowConfigurationCreated(DomainEvent):
    """工作流配置创建事件"""
    workflow_name: str
    workflow_type: str
    step_count: int
    has_auto_approval: bool
    priority_level: int
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowConfiguration"
        self.event_type = "WorkflowConfigurationCreated"
        self.event_version = 1


@dataclass
class WorkflowConfigurationUpdated(DomainEvent):
    """工作流配置更新事件"""
    workflow_name: str
    workflow_type: str
    previous_version: int
    new_version: int
    changes: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowConfiguration"
        self.event_type = "WorkflowConfigurationUpdated"
        self.event_version = 1


@dataclass
class WorkflowExecutionStarted(DomainEvent):
    """工作流执行开始事件"""
    workflow_config_id: str
    execution_id: str
    target_entity_type: str
    target_entity_id: str
    trigger_condition: str
    initial_context: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowExecution"
        self.event_type = "WorkflowExecutionStarted"
        self.event_version = 1


@dataclass
class WorkflowStepCompleted(DomainEvent):
    """工作流步骤完成事件"""
    execution_id: str
    step_name: str
    step_type: str
    step_result: str
    execution_time_ms: int
    output_data: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowExecution"
        self.event_type = "WorkflowStepCompleted"
        self.event_version = 1


@dataclass
class WorkflowStepFailed(DomainEvent):
    """工作流步骤失败事件"""
    execution_id: str
    step_name: str
    step_type: str
    error_message: str
    error_details: Dict[str, Any]
    retry_count: int
    will_retry: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowExecution"
        self.event_type = "WorkflowStepFailed"
        self.event_version = 1


@dataclass
class WorkflowExecutionCompleted(DomainEvent):
    """工作流执行完成事件"""
    execution_id: str
    workflow_config_id: str
    execution_status: str
    total_steps: int
    completed_steps: int
    total_execution_time_ms: int
    final_result: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowExecution"
        self.event_type = "WorkflowExecutionCompleted"
        self.event_version = 1


@dataclass
class WorkflowExecutionTimeout(DomainEvent):
    """工作流执行超时事件"""
    execution_id: str
    workflow_config_id: str
    timeout_step: str
    timeout_seconds: int
    partial_results: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "WorkflowExecution"
        self.event_type = "WorkflowExecutionTimeout"
        self.event_version = 1


# ===== 空间配置事件 =====

@dataclass
class SpatialConfigurationCreated(DomainEvent):
    """空间配置创建事件"""
    config_name: str
    spatial_levels: List[str]
    entity_count: int
    has_access_control: bool
    has_device_integration: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "SpatialConfiguration"
        self.event_type = "SpatialConfigurationCreated"
        self.event_version = 1


@dataclass
class SpatialEntityCreated(DomainEvent):
    """空间实体创建事件"""
    spatial_config_id: str
    entity_type: str
    entity_level: int
    entity_code: str
    entity_name: str
    parent_id: Optional[str]
    has_access_control: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "SpatialEntity"
        self.event_type = "SpatialEntityCreated"
        self.event_version = 1


@dataclass
class SpatialEntityUpdated(DomainEvent):
    """空间实体更新事件"""
    spatial_config_id: str
    entity_type: str
    entity_code: str
    changes: Dict[str, Any]
    access_control_changed: bool
    device_integration_changed: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "SpatialEntity"
        self.event_type = "SpatialEntityUpdated"
        self.event_version = 1


@dataclass
class SpatialAccessControlUpdated(DomainEvent):
    """空间访问控制更新事件"""
    entity_id: str
    entity_type: str
    entity_path: str
    previous_rules: Dict[str, Any]
    new_rules: Dict[str, Any]
    affected_users: List[str]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "SpatialEntity"
        self.event_type = "SpatialAccessControlUpdated"
        self.event_version = 1


@dataclass
class SpatialHierarchyChanged(DomainEvent):
    """空间层级结构变更事件"""
    affected_entities: List[str]
    operation_type: str  # move, add_child, remove_child
    parent_id: Optional[str]
    child_id: str
    new_hierarchy_path: str
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "SpatialEntity"
        self.event_type = "SpatialHierarchyChanged"
        self.event_version = 1


# ===== 业务规则事件 =====

@dataclass
class BusinessRuleCreated(DomainEvent):
    """业务规则创建事件"""
    rule_name: str
    rule_category: str
    rule_priority: int
    condition_count: int
    action_count: int
    is_active: bool
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "BusinessRule"
        self.event_type = "BusinessRuleCreated"
        self.event_version = 1


@dataclass
class BusinessRuleUpdated(DomainEvent):
    """业务规则更新事件"""
    rule_name: str
    rule_category: str
    previous_version: int
    new_version: int
    changes: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "BusinessRule"
        self.event_type = "BusinessRuleUpdated"
        self.event_version = 1


@dataclass
class BusinessRuleExecuted(DomainEvent):
    """业务规则执行事件"""
    rule_id: str
    rule_name: str
    target_entity_type: str
    target_entity_id: str
    execution_result: str
    execution_time_ms: int
    conditions_evaluated: List[Dict[str, Any]]
    actions_executed: List[Dict[str, Any]]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "BusinessRule"
        self.event_type = "BusinessRuleExecuted"
        self.event_version = 1


@dataclass
class BusinessRuleActivated(DomainEvent):
    """业务规则激活事件"""
    rule_name: str
    rule_category: str
    effective_from: datetime
    affected_entities: List[str]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "BusinessRule"
        self.event_type = "BusinessRuleActivated"
        self.event_version = 1


@dataclass
class BusinessRuleDeactivated(DomainEvent):
    """业务规则停用事件"""
    rule_name: str
    rule_category: str
    reason: str
    effective_until: datetime
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "BusinessRule"
        self.event_type = "BusinessRuleDeactivated"
        self.event_version = 1


# ===== 配置验证事件 =====

@dataclass
class ConfigurationValidated(DomainEvent):
    """配置验证事件"""
    config_type: str
    config_id: str
    validation_result: str  # success, warning, error
    validation_errors: List[Dict[str, Any]]
    validation_warnings: List[Dict[str, Any]]
    validation_duration_ms: int
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "Configuration"
        self.event_type = "ConfigurationValidated"
        self.event_version = 1


@dataclass
class ConfigurationCacheInvalidated(DomainEvent):
    """配置缓存失效事件"""
    config_type: str
    config_id: str
    cache_keys: List[str]
    invalidation_reason: str
    affected_tenants: List[str]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "Configuration"
        self.event_type = "ConfigurationCacheInvalidated"
        self.event_version = 1


@dataclass
class ConfigurationSyncRequired(DomainEvent):
    """配置同步需求事件"""
    config_type: str
    config_id: str
    change_type: str  # create, update, delete
    target_instances: List[str]
    sync_priority: int
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "Configuration"
        self.event_type = "ConfigurationSyncRequired"
        self.event_version = 1


# ===== 配置版本事件 =====

@dataclass
class ConfigurationVersionCreated(DomainEvent):
    """配置版本创建事件"""
    config_id: str
    config_type: str
    version_number: int
    change_description: str
    snapshot_size_bytes: int
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "ConfigurationVersion"
        self.event_type = "ConfigurationVersionCreated"
        self.event_version = 1


@dataclass
class ConfigurationRolledBack(DomainEvent):
    """配置回滚事件"""
    config_id: str
    config_type: str
    from_version: int
    to_version: int
    rollback_reason: str
    affected_components: List[str]
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_type = "ConfigurationVersion"
        self.event_type = "ConfigurationRolledBack"
        self.event_version = 1 