"""
访客管理系统 - 领域事件包初始化

导出配置引擎相关的所有领域事件类
"""

from .config_events import (
    # 表单配置事件
    FormConfigurationCreated,
    FormConfigurationUpdated,
    FormConfigurationActivated,
    FormConfigurationDeactivated,
    FormFieldAdded,
    FormFieldUpdated,
    FormFieldRemoved,
    FormValidated,
    FormValidationFailed,
    
    # 工作流配置事件
    WorkflowConfigurationCreated,
    WorkflowConfigurationUpdated,
    WorkflowStepAdded,
    WorkflowStepUpdated,
    WorkflowStepRemoved,
    WorkflowActivated,
    WorkflowDeactivated,
    WorkflowExecutionStarted,
    WorkflowExecutionCompleted,
    WorkflowExecutionFailed,
    WorkflowStepExecuted,
    
    # 空间配置事件
    SpatialConfigurationCreated,
    SpatialConfigurationUpdated,
    SpatialEntityCreated,
    SpatialEntityUpdated,
    SpatialEntityRemoved,
    SpatialRelationshipCreated,
    SpatialRelationshipUpdated,
    SpatialRelationshipRemoved,
    SpatialHierarchyUpdated,
    
    # 业务规则事件
    BusinessRuleCreated,
    BusinessRuleUpdated,
    BusinessRuleActivated,
    BusinessRuleDeactivated,
    BusinessRuleExecuted,
    BusinessRuleExecutionFailed,
    RuleConditionEvaluated,
    RuleActionExecuted
)

__all__ = [
    # 表单配置事件
    "FormConfigurationCreated",
    "FormConfigurationUpdated", 
    "FormConfigurationActivated",
    "FormConfigurationDeactivated",
    "FormFieldAdded",
    "FormFieldUpdated",
    "FormFieldRemoved",
    "FormValidated",
    "FormValidationFailed",
    
    # 工作流配置事件
    "WorkflowConfigurationCreated",
    "WorkflowConfigurationUpdated",
    "WorkflowStepAdded",
    "WorkflowStepUpdated",
    "WorkflowStepRemoved",
    "WorkflowActivated",
    "WorkflowDeactivated",
    "WorkflowExecutionStarted",
    "WorkflowExecutionCompleted",
    "WorkflowExecutionFailed",
    "WorkflowStepExecuted",
    
    # 空间配置事件
    "SpatialConfigurationCreated",
    "SpatialConfigurationUpdated",
    "SpatialEntityCreated",
    "SpatialEntityUpdated",
    "SpatialEntityRemoved",
    "SpatialRelationshipCreated",
    "SpatialRelationshipUpdated",
    "SpatialRelationshipRemoved",
    "SpatialHierarchyUpdated",
    
    # 业务规则事件
    "BusinessRuleCreated",
    "BusinessRuleUpdated",
    "BusinessRuleActivated",
    "BusinessRuleDeactivated",
    "BusinessRuleExecuted",
    "BusinessRuleExecutionFailed",
    "RuleConditionEvaluated",
    "RuleActionExecuted"
] 