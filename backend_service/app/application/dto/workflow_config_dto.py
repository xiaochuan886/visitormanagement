"""
工作流配置相关DTO定义
定义工作流配置系统中的数据传输对象
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from app.domain.enums.config_enums import WorkflowType, WorkflowStatus, StepType, ApprovalType


class WorkflowStepConfigurationDTO(BaseModel):
    """工作流步骤配置DTO"""
    step_name: str = Field(..., description="步骤名称", min_length=1, max_length=100)
    step_type: StepType = Field(..., description="步骤类型")
    step_order: int = Field(..., description="步骤顺序", ge=0)
    step_description: Optional[str] = Field(None, description="步骤描述")
    approver_type: Optional[ApprovalType] = Field(None, description="审批者类型")
    approvers: Optional[List[str]] = Field(None, description="审批者列表")
    timeout_hours: int = Field(24, description="超时时间（小时）", ge=1, le=168)
    conditions: Optional[Dict[str, Any]] = Field(None, description="步骤条件")
    actions: Optional[Dict[str, Any]] = Field(None, description="步骤动作")
    escalation_rules: Optional[Dict[str, Any]] = Field(None, description="升级规则")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    is_optional: bool = Field(False, description="是否可选步骤")
    can_skip: bool = Field(False, description="是否可跳过")
    retry_config: Optional[Dict[str, Any]] = Field(None, description="重试配置")

    @validator('approvers')
    def validate_approvers(cls, v, values):
        """验证审批者配置"""
        approver_type = values.get('approver_type')
        if approver_type and approver_type != ApprovalType.AUTOMATIC:
            if not v or len(v) == 0:
                raise ValueError(f'{approver_type.value} 类型需要指定审批者')
        return v


class WorkflowTriggerConditionDTO(BaseModel):
    """工作流触发条件DTO"""
    condition_name: str = Field(..., description="条件名称")
    field_name: str = Field(..., description="字段名称")
    operator: str = Field(..., description="操作符")
    expected_value: Any = Field(..., description="期望值")
    condition_group: Optional[str] = Field(None, description="条件分组")
    logical_operator: str = Field("AND", description="逻辑操作符（AND/OR）")


class WorkflowConfigurationCreateDTO(BaseModel):
    """工作流配置创建DTO"""
    workflow_name: str = Field(..., description="工作流名称", min_length=2, max_length=100)
    workflow_type: WorkflowType = Field(..., description="工作流类型")
    description: Optional[str] = Field(None, description="工作流描述")
    trigger_conditions: List[WorkflowTriggerConditionDTO] = Field(..., description="触发条件", min_items=1)
    workflow_steps: List[WorkflowStepConfigurationDTO] = Field(..., description="工作流步骤", min_items=1)
    failure_handling: Optional[Dict[str, Any]] = Field(None, description="失败处理策略")
    timeout_settings: Optional[Dict[str, Any]] = Field(None, description="超时设置")
    priority_level: int = Field(1, description="优先级", ge=1, le=10)
    auto_start: bool = Field(True, description="是否自动启动")
    parallel_execution: bool = Field(False, description="是否支持并行执行")

    @validator('workflow_steps')
    def validate_workflow_steps(cls, v):
        """验证工作流步骤"""
        if not v:
            raise ValueError('工作流至少需要包含一个步骤')
        
        # 检查步骤名称重复
        step_names = [step.step_name for step in v]
        if len(step_names) != len(set(step_names)):
            raise ValueError('步骤名称不能重复')
        
        # 检查步骤顺序重复
        step_orders = [step.step_order for step in v]
        if len(step_orders) != len(set(step_orders)):
            raise ValueError('步骤顺序不能重复')
        
        return v


class WorkflowConfigurationUpdateDTO(BaseModel):
    """工作流配置更新DTO"""
    workflow_name: Optional[str] = Field(None, description="工作流名称", min_length=2, max_length=100)
    description: Optional[str] = Field(None, description="工作流描述")
    trigger_conditions: Optional[List[WorkflowTriggerConditionDTO]] = Field(None, description="触发条件")
    workflow_steps: Optional[List[WorkflowStepConfigurationDTO]] = Field(None, description="工作流步骤")
    failure_handling: Optional[Dict[str, Any]] = Field(None, description="失败处理策略")
    timeout_settings: Optional[Dict[str, Any]] = Field(None, description="超时设置")
    priority_level: Optional[int] = Field(None, description="优先级", ge=1, le=10)
    is_active: Optional[bool] = Field(None, description="是否激活")
    auto_start: Optional[bool] = Field(None, description="是否自动启动")
    parallel_execution: Optional[bool] = Field(None, description="是否支持并行执行")


class WorkflowStepResponseDTO(BaseModel):
    """工作流步骤响应DTO"""
    step_name: str = Field(..., description="步骤名称")
    step_type: str = Field(..., description="步骤类型")
    step_order: int = Field(..., description="步骤顺序")
    step_description: Optional[str] = Field(None, description="步骤描述")
    approver_type: Optional[str] = Field(None, description="审批者类型")
    approvers: Optional[List[str]] = Field(None, description="审批者列表")
    timeout_hours: int = Field(..., description="超时时间（小时）")
    conditions: Optional[Dict[str, Any]] = Field(None, description="步骤条件")
    actions: Optional[Dict[str, Any]] = Field(None, description="步骤动作")
    escalation_rules: Optional[Dict[str, Any]] = Field(None, description="升级规则")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    is_optional: bool = Field(..., description="是否可选步骤")
    can_skip: bool = Field(..., description="是否可跳过")
    retry_config: Optional[Dict[str, Any]] = Field(None, description="重试配置")

    class Config:
        from_attributes = True


class WorkflowConfigurationResponseDTO(BaseModel):
    """工作流配置响应DTO"""
    id: UUID = Field(..., description="配置ID")
    workflow_name: str = Field(..., description="工作流名称")
    workflow_type: str = Field(..., description="工作流类型")
    workflow_version: int = Field(..., description="工作流版本")
    description: Optional[str] = Field(None, description="工作流描述")
    trigger_conditions: List[Dict[str, Any]] = Field(..., description="触发条件")
    workflow_steps: List[WorkflowStepResponseDTO] = Field(..., description="工作流步骤")
    failure_handling: Optional[Dict[str, Any]] = Field(None, description="失败处理策略")
    timeout_settings: Optional[Dict[str, Any]] = Field(None, description="超时设置")
    is_active: bool = Field(..., description="是否激活")
    priority_level: int = Field(..., description="优先级")
    auto_start: bool = Field(..., description="是否自动启动")
    parallel_execution: bool = Field(..., description="是否支持并行执行")
    tenant_id: str = Field(..., description="租户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")

    class Config:
        from_attributes = True


class WorkflowExecutionCreateDTO(BaseModel):
    """工作流执行创建DTO"""
    workflow_config_id: UUID = Field(..., description="工作流配置ID")
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    execution_context: Optional[Dict[str, Any]] = Field(None, description="执行上下文")
    initial_data: Optional[Dict[str, Any]] = Field(None, description="初始数据")
    priority_override: Optional[int] = Field(None, description="优先级覆盖", ge=1, le=10)
    force_start: bool = Field(False, description="是否强制启动")


class WorkflowExecutionResponseDTO(BaseModel):
    """工作流执行响应DTO"""
    id: UUID = Field(..., description="执行ID")
    workflow_config_id: UUID = Field(..., description="工作流配置ID")
    target_entity_type: str = Field(..., description="目标实体类型")
    target_entity_id: str = Field(..., description="目标实体ID")
    execution_status: str = Field(..., description="执行状态")
    current_step: int = Field(..., description="当前步骤")
    execution_data: Optional[Dict[str, Any]] = Field(None, description="执行数据")
    step_results: Optional[Dict[str, Any]] = Field(None, description="步骤结果")
    context_data: Optional[Dict[str, Any]] = Field(None, description="上下文数据")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    last_executed_at: Optional[datetime] = Field(None, description="最后执行时间")
    error_details: Optional[str] = Field(None, description="错误详情")
    retry_count: int = Field(..., description="重试次数")
    tenant_id: str = Field(..., description="租户ID")

    class Config:
        from_attributes = True


class WorkflowExecutionQueryDTO(BaseModel):
    """工作流执行查询DTO"""
    workflow_config_id: Optional[UUID] = Field(None, description="工作流配置ID")
    target_entity_type: Optional[str] = Field(None, description="目标实体类型")
    target_entity_id: Optional[str] = Field(None, description="目标实体ID")
    execution_status: Optional[WorkflowStatus] = Field(None, description="执行状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class WorkflowExecutionListResponseDTO(BaseModel):
    """工作流执行列表响应DTO"""
    items: List[WorkflowExecutionResponseDTO] = Field(..., description="执行列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数")


class WorkflowStepExecutionDTO(BaseModel):
    """工作流步骤执行DTO"""
    execution_id: UUID = Field(..., description="执行ID")
    step_name: str = Field(..., description="步骤名称")
    action: str = Field(..., description="执行动作（approve/reject/skip）")
    comment: Optional[str] = Field(None, description="执行备注")
    execution_data: Optional[Dict[str, Any]] = Field(None, description="执行数据")
    approver_id: Optional[str] = Field(None, description="审批者ID")


class WorkflowStepExecutionResultDTO(BaseModel):
    """工作流步骤执行结果DTO"""
    execution_id: UUID = Field(..., description="执行ID")
    step_name: str = Field(..., description="步骤名称")
    execution_result: str = Field(..., description="执行结果")
    execution_time_ms: int = Field(..., description="执行耗时（毫秒）")
    output_data: Dict[str, Any] = Field(..., description="输出数据")
    next_step: Optional[str] = Field(None, description="下一步骤")
    workflow_completed: bool = Field(..., description="工作流是否完成")


class WorkflowAnalyticsDTO(BaseModel):
    """工作流分析DTO"""
    workflow_config_id: UUID = Field(..., description="工作流配置ID")
    total_executions: int = Field(..., description="总执行次数")
    success_rate: float = Field(..., description="成功率")
    average_execution_time_ms: int = Field(..., description="平均执行时间（毫秒）")
    most_failed_step: Optional[str] = Field(None, description="最常失败的步骤")
    bottleneck_steps: List[str] = Field(..., description="瓶颈步骤列表")
    execution_trends: List[Dict[str, Any]] = Field(..., description="执行趋势数据")


class WorkflowTemplateDTO(BaseModel):
    """工作流模板DTO"""
    template_name: str = Field(..., description="模板名称")
    template_category: str = Field(..., description="模板分类")
    workflow_type: WorkflowType = Field(..., description="工作流类型")
    template_description: str = Field(..., description="模板描述")
    template_config: Dict[str, Any] = Field(..., description="模板配置")
    is_system_template: bool = Field(False, description="是否系统模板")
    tags: List[str] = Field([], description="标签列表")
    usage_count: int = Field(0, description="使用次数")


class WorkflowConfigurationListResponseDTO(BaseModel):
    """工作流配置列表响应DTO"""
    items: List[WorkflowConfigurationResponseDTO] = Field(..., description="配置列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="页大小")
    total_pages: int = Field(..., description="总页数")


class WorkflowConfigurationQueryDTO(BaseModel):
    """工作流配置查询DTO"""
    workflow_type: Optional[WorkflowType] = Field(None, description="工作流类型")
    workflow_name: Optional[str] = Field(None, description="工作流名称（模糊搜索）")
    is_active: Optional[bool] = Field(None, description="是否激活")
    priority_level: Optional[int] = Field(None, description="优先级", ge=1, le=10)
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(20, description="页大小", ge=1, le=100)


class WorkflowValidationResultDTO(BaseModel):
    """工作流验证结果DTO"""
    is_valid: bool = Field(..., description="是否验证通过")
    errors: List[Dict[str, Any]] = Field(..., description="错误信息列表")
    warnings: List[Dict[str, Any]] = Field(..., description="警告信息列表")
    step_errors: Dict[str, List[str]] = Field(..., description="步骤错误详情")
    validation_duration_ms: int = Field(..., description="验证耗时（毫秒）")


class WorkflowExportDTO(BaseModel):
    """工作流导出DTO"""
    export_format: str = Field("json", description="导出格式")
    include_steps: bool = Field(True, description="是否包含步骤配置")
    include_conditions: bool = Field(True, description="是否包含触发条件")
    include_execution_history: bool = Field(False, description="是否包含执行历史")
    compress_output: bool = Field(False, description="是否压缩输出") 