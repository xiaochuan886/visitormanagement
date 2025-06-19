"""
场景管理系统 DTO 数据传输对象
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class ScenarioTemplateCategory(str, Enum):
    """场景模板分类枚举"""
    VISITOR_MANAGEMENT = "visitor_management"
    EMPLOYEE_MANAGEMENT = "employee_management" 
    EVENT_MANAGEMENT = "event_management"
    SECURITY_MANAGEMENT = "security_management"
    CUSTOM = "custom"


class ScenarioInstanceStatus(str, Enum):
    """场景实例状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    TESTING = "testing"


class ScenarioExecutionStatus(str, Enum):
    """场景执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ScenarioExecutionType(str, Enum):
    """场景执行类型枚举"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"
    TEST = "test"


class TriggerSource(str, Enum):
    """触发源枚举"""
    API = "api"
    UI = "ui"
    SYSTEM = "system"
    WORKFLOW = "workflow"
    SCHEDULER = "scheduler"
    WEBHOOK = "webhook"


# ================== 场景模板 DTO ==================

class ScenarioTemplateCreateDTO(BaseModel):
    """创建场景模板DTO"""
    template_name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    template_code: str = Field(..., min_length=1, max_length=50, description="模板代码")
    template_category: ScenarioTemplateCategory = Field(..., description="模板分类")
    template_description: Optional[str] = Field(None, description="模板描述")
    
    # 场景特征定义
    scenario_features: Dict[str, Any] = Field(..., description="场景特征配置")
    default_configurations: Dict[str, Any] = Field(..., description="默认配置集合")
    
    # 模板元数据
    supported_roles: Optional[List[str]] = Field(None, description="支持的角色类型")
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="触发条件模板")
    template_tags: Optional[List[str]] = Field(None, description="模板标签")
    
    is_builtin: bool = Field(False, description="是否为内置模板")
    
    @validator('template_code')
    def validate_template_code(cls, v):
        """验证模板代码格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('模板代码只能包含字母、数字、下划线和连字符')
        return v.lower()


class ScenarioTemplateUpdateDTO(BaseModel):
    """更新场景模板DTO"""
    template_name: Optional[str] = Field(None, min_length=1, max_length=100)
    template_description: Optional[str] = Field(None)
    scenario_features: Optional[Dict[str, Any]] = Field(None)
    default_configurations: Optional[Dict[str, Any]] = Field(None)
    supported_roles: Optional[List[str]] = Field(None)
    trigger_conditions: Optional[Dict[str, Any]] = Field(None)
    template_tags: Optional[List[str]] = Field(None)
    is_template_active: Optional[bool] = Field(None)


class ScenarioTemplateResponseDTO(BaseModel):
    """场景模板响应DTO"""
    id: UUID
    template_name: str
    template_code: str
    template_version: int
    template_category: ScenarioTemplateCategory
    template_description: Optional[str]
    
    is_builtin: bool
    is_template_active: bool
    
    scenario_features: Dict[str, Any]
    default_configurations: Dict[str, Any]
    supported_roles: Optional[List[str]]
    trigger_conditions: Optional[Dict[str, Any]]
    template_tags: Optional[List[str]]
    
    usage_count: int
    last_used_at: Optional[datetime]
    
    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    tenant_id: str
    
    class Config:
        from_attributes = True


# ================== 场景实例 DTO ==================

class ScenarioInstanceCreateDTO(BaseModel):
    """创建场景实例DTO"""
    instance_name: str = Field(..., min_length=1, max_length=100, description="实例名称")
    instance_code: str = Field(..., min_length=1, max_length=50, description="实例代码")
    template_id: UUID = Field(..., description="模板ID")
    
    priority_level: int = Field(1, ge=1, le=10, description="优先级")
    
    # 场景配置覆盖
    custom_configurations: Optional[Dict[str, Any]] = Field(None, description="自定义配置")
    form_config_overrides: Optional[Dict[str, Any]] = Field(None, description="表单配置覆盖")
    workflow_config_overrides: Optional[Dict[str, Any]] = Field(None, description="工作流配置覆盖")
    business_rule_overrides: Optional[Dict[str, Any]] = Field(None, description="业务规则覆盖")
    spatial_config_overrides: Optional[Dict[str, Any]] = Field(None, description="空间配置覆盖")
    
    # 路由和触发
    routing_rules: Dict[str, Any] = Field(..., description="路由规则")
    trigger_conditions: Dict[str, Any] = Field(..., description="触发条件")
    auto_routing_enabled: bool = Field(True, description="是否启用自动路由")
    
    # 使用范围
    applicable_sites: Optional[List[str]] = Field(None, description="适用站点")
    applicable_departments: Optional[List[str]] = Field(None, description="适用部门")
    applicable_roles: Optional[List[str]] = Field(None, description="适用角色")
    
    # 时间有效性
    effective_from: Optional[datetime] = Field(None, description="生效时间")
    effective_until: Optional[datetime] = Field(None, description="失效时间")
    
    @validator('instance_code')
    def validate_instance_code(cls, v):
        """验证实例代码格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('实例代码只能包含字母、数字、下划线和连字符')
        return v.lower()
    
    @validator('effective_until')
    def validate_effective_dates(cls, v, values):
        """验证有效期"""
        if v and 'effective_from' in values and values['effective_from']:
            if v <= values['effective_from']:
                raise ValueError('失效时间必须晚于生效时间')
        return v


class ScenarioInstanceUpdateDTO(BaseModel):
    """更新场景实例DTO"""
    instance_name: Optional[str] = Field(None, min_length=1, max_length=100)
    instance_status: Optional[ScenarioInstanceStatus] = Field(None)
    priority_level: Optional[int] = Field(None, ge=1, le=10)
    
    custom_configurations: Optional[Dict[str, Any]] = Field(None)
    form_config_overrides: Optional[Dict[str, Any]] = Field(None)
    workflow_config_overrides: Optional[Dict[str, Any]] = Field(None)
    business_rule_overrides: Optional[Dict[str, Any]] = Field(None)
    spatial_config_overrides: Optional[Dict[str, Any]] = Field(None)
    
    routing_rules: Optional[Dict[str, Any]] = Field(None)
    trigger_conditions: Optional[Dict[str, Any]] = Field(None)
    auto_routing_enabled: Optional[bool] = Field(None)
    
    applicable_sites: Optional[List[str]] = Field(None)
    applicable_departments: Optional[List[str]] = Field(None)
    applicable_roles: Optional[List[str]] = Field(None)
    
    effective_from: Optional[datetime] = Field(None)
    effective_until: Optional[datetime] = Field(None)


class ScenarioInstanceResponseDTO(BaseModel):
    """场景实例响应DTO"""
    id: UUID
    instance_name: str
    instance_code: str
    template_id: UUID
    
    instance_status: ScenarioInstanceStatus
    priority_level: int
    
    # 配置信息
    custom_configurations: Optional[Dict[str, Any]]
    form_config_overrides: Optional[Dict[str, Any]]
    workflow_config_overrides: Optional[Dict[str, Any]]
    business_rule_overrides: Optional[Dict[str, Any]]
    spatial_config_overrides: Optional[Dict[str, Any]]
    
    # 路由和触发
    routing_rules: Dict[str, Any]
    trigger_conditions: Dict[str, Any]
    auto_routing_enabled: bool
    
    # 使用范围
    applicable_sites: Optional[List[str]]
    applicable_departments: Optional[List[str]]
    applicable_roles: Optional[List[str]]
    
    # 时间有效性
    effective_from: Optional[datetime]
    effective_until: Optional[datetime]
    
    # 统计信息
    execution_count: int
    success_count: int
    last_executed_at: Optional[datetime]
    average_execution_time: Optional[float]
    
    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    tenant_id: str
    
    # 关联模板信息
    template: Optional[ScenarioTemplateResponseDTO] = None
    
    class Config:
        from_attributes = True


# ================== 场景执行 DTO ==================

class ScenarioExecutionCreateDTO(BaseModel):
    """创建场景执行DTO"""
    scenario_instance_id: UUID = Field(..., description="场景实例ID")
    execution_type: ScenarioExecutionType = Field(..., description="执行类型")
    
    # 触发信息
    trigger_source: Optional[TriggerSource] = Field(None, description="触发源")
    trigger_user_id: Optional[str] = Field(None, description="触发用户")
    trigger_context: Optional[Dict[str, Any]] = Field(None, description="触发上下文")
    
    # 目标实体
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    target_entity_data: Optional[Dict[str, Any]] = Field(None, description="目标实体数据快照")


class ScenarioExecutionUpdateDTO(BaseModel):
    """更新场景执行DTO"""
    execution_status: Optional[ScenarioExecutionStatus] = Field(None)
    current_step: Optional[str] = Field(None)
    execution_data: Optional[Dict[str, Any]] = Field(None)
    step_results: Optional[Dict[str, Any]] = Field(None)
    execution_result: Optional[Dict[str, Any]] = Field(None)
    error_details: Optional[str] = Field(None)


class ScenarioExecutionResponseDTO(BaseModel):
    """场景执行响应DTO"""
    id: UUID
    scenario_instance_id: UUID
    
    # 执行信息
    execution_status: ScenarioExecutionStatus
    execution_type: ScenarioExecutionType
    
    # 触发信息
    trigger_source: Optional[TriggerSource]
    trigger_user_id: Optional[str]
    trigger_context: Optional[Dict[str, Any]]
    
    # 目标实体
    target_entity_type: str
    target_entity_id: str
    target_entity_data: Optional[Dict[str, Any]]
    
    # 执行过程
    execution_steps: Optional[Dict[str, Any]]
    current_step: Optional[str]
    execution_data: Optional[Dict[str, Any]]
    step_results: Optional[Dict[str, Any]]
    
    # 时间信息
    started_at: datetime
    completed_at: Optional[datetime]
    execution_duration: Optional[float]
    
    # 结果信息
    execution_result: Optional[Dict[str, Any]]
    error_details: Optional[str]
    retry_count: int
    
    # 审计字段
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    
    # 关联场景实例信息
    scenario_instance: Optional[ScenarioInstanceResponseDTO] = None
    
    class Config:
        from_attributes = True


# ================== 场景路由规则 DTO ==================

class ScenarioRoutingRuleCreateDTO(BaseModel):
    """创建场景路由规则DTO"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    rule_description: Optional[str] = Field(None, description="规则描述")
    
    rule_priority: int = Field(1, ge=1, le=100, description="规则优先级")
    rule_conditions: Dict[str, Any] = Field(..., description="路由条件")
    target_scenario_ids: List[UUID] = Field(..., description="目标场景ID列表")
    
    condition_logic: str = Field("AND", description="条件逻辑")
    match_strategy: str = Field("first_match", description="匹配策略")
    
    effective_from: Optional[datetime] = Field(None, description="生效时间")
    effective_until: Optional[datetime] = Field(None, description="失效时间")
    
    @validator('condition_logic')
    def validate_condition_logic(cls, v):
        if v not in ['AND', 'OR']:
            raise ValueError('条件逻辑必须是 AND 或 OR')
        return v
    
    @validator('match_strategy')
    def validate_match_strategy(cls, v):
        if v not in ['first_match', 'best_match', 'all_match', 'weighted_match']:
            raise ValueError('匹配策略无效')
        return v


class ScenarioRoutingRuleUpdateDTO(BaseModel):
    """更新场景路由规则DTO"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100)
    rule_description: Optional[str] = Field(None)
    rule_priority: Optional[int] = Field(None, ge=1, le=100)
    rule_conditions: Optional[Dict[str, Any]] = Field(None)
    target_scenario_ids: Optional[List[UUID]] = Field(None)
    condition_logic: Optional[str] = Field(None)
    match_strategy: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    effective_from: Optional[datetime] = Field(None)
    effective_until: Optional[datetime] = Field(None)


class ScenarioRoutingRuleResponseDTO(BaseModel):
    """场景路由规则响应DTO"""
    id: UUID
    rule_name: str
    rule_description: Optional[str]
    
    rule_priority: int
    rule_conditions: Dict[str, Any]
    target_scenario_ids: List[UUID]
    
    condition_logic: str
    match_strategy: str
    
    is_active: bool
    effective_from: Optional[datetime]
    effective_until: Optional[datetime]
    
    # 统计信息
    matched_count: int
    success_count: int
    last_matched_at: Optional[datetime]
    
    # 审计字段
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    tenant_id: str
    
    class Config:
        from_attributes = True


# ================== 场景分析 DTO ==================

class ScenarioAnalyticsResponseDTO(BaseModel):
    """场景分析响应DTO"""
    id: UUID
    scenario_instance_id: UUID
    
    analytics_date: datetime
    period_type: str
    
    # 执行统计
    total_executions: int
    successful_executions: int
    failed_executions: int
    
    # 性能统计
    avg_execution_time: float
    min_execution_time: Optional[float]
    max_execution_time: Optional[float]
    
    # 用户统计
    unique_users: int
    user_distribution: Optional[Dict[str, Any]]
    
    # 时间分布
    hourly_distribution: Optional[Dict[str, Any]]
    daily_trend: Optional[Dict[str, Any]]
    
    # 业务指标
    business_metrics: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


# ================== 查询和分页 DTO ==================

class ScenarioTemplateQueryDTO(BaseModel):
    """场景模板查询DTO"""
    template_category: Optional[ScenarioTemplateCategory] = None
    is_builtin: Optional[bool] = None
    is_template_active: Optional[bool] = None
    template_tags: Optional[List[str]] = None
    search: Optional[str] = None


class ScenarioInstanceQueryDTO(BaseModel):
    """场景实例查询DTO"""
    template_id: Optional[UUID] = None
    instance_status: Optional[ScenarioInstanceStatus] = None
    applicable_sites: Optional[List[str]] = None
    applicable_departments: Optional[List[str]] = None
    applicable_roles: Optional[List[str]] = None
    auto_routing_enabled: Optional[bool] = None
    search: Optional[str] = None


class ScenarioExecutionQueryDTO(BaseModel):
    """场景执行查询DTO"""
    scenario_instance_id: Optional[UUID] = None
    execution_status: Optional[ScenarioExecutionStatus] = None
    execution_type: Optional[ScenarioExecutionType] = None
    trigger_source: Optional[TriggerSource] = None
    target_entity_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ================== 批量操作 DTO ==================

class ScenarioInstanceBatchUpdateDTO(BaseModel):
    """场景实例批量更新DTO"""
    instance_ids: List[UUID] = Field(..., description="实例ID列表")
    update_data: ScenarioInstanceUpdateDTO = Field(..., description="更新数据")


class ScenarioInstanceBatchActivateDTO(BaseModel):
    """场景实例批量激活DTO"""
    instance_ids: List[UUID] = Field(..., description="实例ID列表")
    activate: bool = Field(True, description="是否激活")


# ================== 场景复制和导入导出 DTO ==================

class ScenarioInstanceCloneDTO(BaseModel):
    """场景实例克隆DTO"""
    source_instance_id: UUID = Field(..., description="源实例ID")
    new_instance_name: str = Field(..., description="新实例名称")
    new_instance_code: str = Field(..., description="新实例代码")
    clone_executions: bool = Field(False, description="是否克隆执行历史")


class ScenarioTemplateExportDTO(BaseModel):
    """场景模板导出DTO"""
    template_ids: List[UUID] = Field(..., description="模板ID列表")
    include_instances: bool = Field(False, description="是否包含实例")
    include_analytics: bool = Field(False, description="是否包含分析数据")


class ScenarioTemplateImportDTO(BaseModel):
    """场景模板导入DTO"""
    template_data: Dict[str, Any] = Field(..., description="模板数据")
    conflict_resolution: str = Field("skip", description="冲突解决策略")  # skip, overwrite, merge
    
    @validator('conflict_resolution')
    def validate_conflict_resolution(cls, v):
        if v not in ['skip', 'overwrite', 'merge']:
            raise ValueError('冲突解决策略必须是 skip, overwrite 或 merge')
        return v 