"""
业务规则相关DTO定义
定义业务规则引擎中的数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from uuid import UUID

from app.domain.enums.config_enums import BusinessRuleCategory, RuleExecutionResult, ValidationSeverity


class RuleConditionDTO(BaseModel):
    """规则条件DTO"""
    condition_id: str = Field(..., description="条件ID", min_length=1, max_length=50)
    field_name: str = Field(..., description="字段名称")
    operator: str = Field(..., description="操作符")
    expected_value: Union[str, int, float, bool, List[Any]] = Field(..., description="期望值")
    condition_type: str = Field("simple", description="条件类型（simple/complex/function）")
    condition_group: Optional[str] = Field(None, description="条件分组")
    logical_operator: str = Field("AND", description="逻辑操作符（AND/OR/NOT）")
    weight: float = Field(1.0, description="条件权重", ge=0.0, le=1.0)
    description: Optional[str] = Field(None, description="条件描述")

    @validator('operator')
    def validate_operator(cls, v):
        """验证操作符"""
        valid_operators = [
            'eq', 'ne', 'gt', 'gte', 'lt', 'lte',
            'in', 'not_in', 'contains', 'not_contains',
            'starts_with', 'ends_with', 'regex',
            'is_null', 'is_not_null', 'is_empty', 'is_not_empty'
        ]
        if v not in valid_operators:
            raise ValueError(f'不支持的操作符: {v}')
        return v


class RuleActionDTO(BaseModel):
    """规则动作DTO"""
    action_id: str = Field(..., description="动作ID", min_length=1, max_length=50)
    action_type: str = Field(..., description="动作类型")
    action_config: Dict[str, Any] = Field(..., description="动作配置")
    execution_order: int = Field(..., description="执行顺序", ge=0)
    is_async: bool = Field(False, description="是否异步执行")
    timeout_seconds: Optional[int] = Field(None, description="超时时间（秒）", ge=1)
    retry_config: Optional[Dict[str, Any]] = Field(None, description="重试配置")
    error_handling: Optional[Dict[str, Any]] = Field(None, description="错误处理配置")
    description: Optional[str] = Field(None, description="动作描述")

    @validator('action_type')
    def validate_action_type(cls, v):
        """验证动作类型"""
        valid_action_types = [
            'notification', 'workflow_trigger', 'data_update',
            'validation', 'calculation', 'approval_request',
            'device_control', 'email_send', 'webhook_call',
            'log_event', 'cache_update', 'script_execution'
        ]
        if v not in valid_action_types:
            raise ValueError(f'不支持的动作类型: {v}')
        return v


class BusinessRuleCreateDTO(BaseModel):
    """业务规则创建DTO"""
    rule_name: str = Field(..., description="规则名称", min_length=2, max_length=100)
    rule_category: BusinessRuleCategory = Field(..., description="规则类别")
    description: Optional[str] = Field(None, description="规则描述")
    conditions: List[RuleConditionDTO] = Field(..., description="规则条件", min_items=1)
    actions: List[RuleActionDTO] = Field(..., description="规则动作", min_items=1)
    priority: int = Field(1, description="优先级", ge=1, le=10)
    is_active: bool = Field(True, description="是否激活")
    effective_from: Optional[datetime] = Field(None, description="生效开始时间")
    effective_until: Optional[datetime] = Field(None, description="生效结束时间")
    execution_mode: str = Field("immediate", description="执行模式（immediate/scheduled/triggered）")
    target_entities: Optional[List[str]] = Field(None, description="目标实体类型列表")
    tags: List[str] = Field([], description="标签列表")

    @validator('conditions')
    def validate_conditions(cls, v):
        """验证规则条件"""
        if not v:
            raise ValueError('规则至少需要包含一个条件')
        
        # 检查条件ID重复
        condition_ids = [cond.condition_id for cond in v]
        if len(condition_ids) != len(set(condition_ids)):
            raise ValueError('条件ID不能重复')
        
        return v

    @validator('actions')
    def validate_actions(cls, v):
        """验证规则动作"""
        if not v:
            raise ValueError('规则至少需要包含一个动作')
        
        # 检查动作ID重复
        action_ids = [action.action_id for action in v]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError('动作ID不能重复')
        
        # 检查执行顺序重复
        execution_orders = [action.execution_order for action in v]
        if len(execution_orders) != len(set(execution_orders)):
            raise ValueError('动作执行顺序不能重复')
        
        return v

    @validator('effective_until')
    def validate_effective_period(cls, v, values):
        """验证生效期间"""
        effective_from = values.get('effective_from')
        if effective_from and v and v <= effective_from:
            raise ValueError('生效结束时间必须晚于开始时间')
        return v


class BusinessRuleUpdateDTO(BaseModel):
    """业务规则更新DTO"""
    rule_name: Optional[str] = Field(None, description="规则名称", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="规则描述")
    conditions: Optional[List[RuleConditionDTO]] = Field(None, description="规则条件")
    actions: Optional[List[RuleActionDTO]] = Field(None, description="规则动作")
    priority: Optional[int] = Field(None, description="优先级", ge=1, le=10)
    is_active: Optional[bool] = Field(None, description="是否激活")
    effective_from: Optional[datetime] = Field(None, description="生效开始时间")
    effective_until: Optional[datetime] = Field(None, description="生效结束时间")
    execution_mode: Optional[str] = Field(None, description="执行模式")
    target_entities: Optional[List[str]] = Field(None, description="目标实体类型列表")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class BusinessRuleResponseDTO(BaseModel):
    """业务规则响应DTO"""
    id: UUID = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    rule_category: str = Field(..., description="规则类别")
    rule_version: int = Field(..., description="规则版本")
    description: Optional[str] = Field(None, description="规则描述")
    conditions: List[Dict[str, Any]] = Field(..., description="规则条件")
    actions: List[Dict[str, Any]] = Field(..., description="规则动作")
    priority: int = Field(..., description="优先级")
    is_active: bool = Field(..., description="是否激活")
    effective_from: Optional[datetime] = Field(None, description="生效开始时间")
    effective_until: Optional[datetime] = Field(None, description="生效结束时间")
    execution_mode: str = Field(..., description="执行模式")
    target_entities: Optional[List[str]] = Field(None, description="目标实体类型列表")
    tags: List[str] = Field(..., description="标签列表")
    execution_count: int = Field(..., description="执行次数")
    last_executed_at: Optional[datetime] = Field(None, description="最后执行时间")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")

    class Config:
        from_attributes = True


class BusinessRuleExecutionRequestDTO(BaseModel):
    """业务规则执行请求DTO"""
    rule_id: UUID = Field(..., description="规则ID")
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    execution_context: Optional[Dict[str, Any]] = Field(None, description="执行上下文")
    dry_run: bool = Field(False, description="是否试运行")
    force_execution: bool = Field(False, description="是否强制执行")


class RuleConditionResultDTO(BaseModel):
    """规则条件执行结果DTO"""
    condition_id: str = Field(..., description="条件ID")
    condition_name: str = Field(..., description="条件名称")
    evaluation_result: bool = Field(..., description="评估结果")
    actual_value: Any = Field(..., description="实际值")
    expected_value: Any = Field(..., description="期望值")
    operator: str = Field(..., description="操作符")
    evaluation_time_ms: int = Field(..., description="评估耗时（毫秒）")
    error_message: Optional[str] = Field(None, description="错误消息")


class RuleActionResultDTO(BaseModel):
    """规则动作执行结果DTO"""
    action_id: str = Field(..., description="动作ID")
    action_type: str = Field(..., description="动作类型")
    execution_result: RuleExecutionResult = Field(..., description="执行结果")
    execution_time_ms: int = Field(..., description="执行耗时（毫秒）")
    output_data: Optional[Dict[str, Any]] = Field(None, description="输出数据")
    error_message: Optional[str] = Field(None, description="错误消息")
    retry_count: int = Field(0, description="重试次数")


class BusinessRuleExecutionResultDTO(BaseModel):
    """业务规则执行结果DTO"""
    execution_id: UUID = Field(..., description="执行ID")
    rule_id: UUID = Field(..., description="规则ID")
    rule_name: str = Field(..., description="规则名称")
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    overall_result: RuleExecutionResult = Field(..., description="总体执行结果")
    execution_start_time: datetime = Field(..., description="执行开始时间")
    execution_end_time: datetime = Field(..., description="执行结束时间")
    total_execution_time_ms: int = Field(..., description="总执行时间（毫秒）")
    condition_results: List[RuleConditionResultDTO] = Field(..., description="条件执行结果")
    action_results: List[RuleActionResultDTO] = Field(..., description="动作执行结果")
    input_data: Dict[str, Any] = Field(..., description="输入数据")
    output_data: Dict[str, Any] = Field(..., description="输出数据")
    error_details: Optional[str] = Field(None, description="错误详情")
    was_dry_run: bool = Field(..., description="是否为试运行")


class BusinessRuleQueryDTO(BaseModel):
    """业务规则查询DTO"""
    rule_category: Optional[BusinessRuleCategory] = Field(None, description="规则类别")
    rule_name: Optional[str] = Field(None, description="规则名称（模糊搜索）")
    is_active: Optional[bool] = Field(None, description="是否激活")
    priority: Optional[int] = Field(None, description="优先级", ge=1, le=10)
    target_entity: Optional[str] = Field(None, description="目标实体类型")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    effective_date: Optional[datetime] = Field(None, description="生效日期筛选")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class BusinessRuleListResponseDTO(BaseModel):
    """业务规则列表响应DTO"""
    items: List[BusinessRuleResponseDTO] = Field(..., description="规则列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数")


class BusinessRuleValidationResultDTO(BaseModel):
    """业务规则验证结果DTO"""
    is_valid: bool = Field(..., description="是否验证通过")
    errors: List[Dict[str, Any]] = Field(..., description="错误信息列表")
    warnings: List[Dict[str, Any]] = Field(..., description="警告信息列表")
    condition_errors: Dict[str, List[str]] = Field(..., description="条件错误详情")
    action_errors: Dict[str, List[str]] = Field(..., description="动作错误详情")
    validation_duration_ms: int = Field(..., description="验证耗时（毫秒）")


class BusinessRuleAnalyticsDTO(BaseModel):
    """业务规则分析DTO"""
    rule_id: UUID = Field(..., description="规则ID")
    total_executions: int = Field(..., description="总执行次数")
    success_rate: float = Field(..., description="成功率")
    average_execution_time_ms: int = Field(..., description="平均执行时间（毫秒）")
    most_failed_condition: Optional[str] = Field(None, description="最常失败的条件")
    most_failed_action: Optional[str] = Field(None, description="最常失败的动作")
    execution_trends: List[Dict[str, Any]] = Field(..., description="执行趋势数据")
    performance_metrics: Dict[str, Any] = Field(..., description="性能指标")


class BusinessRuleTemplateDTO(BaseModel):
    """业务规则模板DTO"""
    template_name: str = Field(..., description="模板名称")
    template_category: BusinessRuleCategory = Field(..., description="模板分类")
    template_description: str = Field(..., description="模板描述")
    template_config: Dict[str, Any] = Field(..., description="模板配置")
    default_conditions: List[RuleConditionDTO] = Field(..., description="默认条件")
    default_actions: List[RuleActionDTO] = Field(..., description="默认动作")
    is_system_template: bool = Field(False, description="是否系统模板")
    usage_count: int = Field(0, description="使用次数")
    tags: List[str] = Field([], description="标签列表")


class RuleTestCaseDTO(BaseModel):
    """规则测试用例DTO"""
    test_name: str = Field(..., description="测试名称")
    test_description: str = Field(..., description="测试描述")
    input_data: Dict[str, Any] = Field(..., description="测试输入数据")
    expected_condition_results: Dict[str, bool] = Field(..., description="期望的条件结果")
    expected_action_results: Dict[str, str] = Field(..., description="期望的动作结果")
    expected_overall_result: RuleExecutionResult = Field(..., description="期望的总体结果")


class RuleTestResultDTO(BaseModel):
    """规则测试结果DTO"""
    test_name: str = Field(..., description="测试名称")
    test_passed: bool = Field(..., description="测试是否通过")
    execution_result: BusinessRuleExecutionResultDTO = Field(..., description="执行结果")
    assertion_results: List[Dict[str, Any]] = Field(..., description="断言结果")
    test_duration_ms: int = Field(..., description="测试耗时（毫秒）")


class BusinessRuleExportDTO(BaseModel):
    """业务规则导出DTO"""
    export_format: str = Field("json", description="导出格式")
    include_conditions: bool = Field(True, description="是否包含条件配置")
    include_actions: bool = Field(True, description="是否包含动作配置")
    include_execution_history: bool = Field(False, description="是否包含执行历史")
    include_analytics: bool = Field(False, description="是否包含分析数据")
    compress_output: bool = Field(False, description="是否压缩输出")


class RuleDependencyDTO(BaseModel):
    """规则依赖关系DTO"""
    rule_id: UUID = Field(..., description="规则ID")
    dependent_rule_id: UUID = Field(..., description="依赖的规则ID")
    dependency_type: str = Field(..., description="依赖类型（prerequisite/conditional/sequential）")
    dependency_config: Optional[Dict[str, Any]] = Field(None, description="依赖配置")


class RuleExecutionHistoryQueryDTO(BaseModel):
    """规则执行历史查询DTO"""
    rule_id: Optional[UUID] = Field(None, description="规则ID")
    target_entity_type: Optional[str] = Field(None, description="目标实体类型")
    target_entity_id: Optional[str] = Field(None, description="目标实体ID")
    execution_result: Optional[RuleExecutionResult] = Field(None, description="执行结果")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class RuleExecutionHistoryResponseDTO(BaseModel):
    """规则执行历史响应DTO"""
    items: List[BusinessRuleExecutionResultDTO] = Field(..., description="执行历史列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数") 