"""
访客管理系统 - 领域异常包初始化

导出配置引擎相关的所有领域异常类
"""

from .config_exceptions import (
    # 基础异常
    ConfigurationException,
    ValidationException,
    ConfigurationNotFoundException,
    ConfigurationVersionException,
    DuplicateConfigurationException,
    PermissionDeniedException,
    
    # 表单配置异常
    FormConfigurationException,
    FormValidationException,
    FormFieldException,
    UnsupportedFieldTypeException,
    
    # 工作流配置异常
    WorkflowException,
    WorkflowConfigurationException,
    WorkflowExecutionException,
    WorkflowTimeoutException,
    WorkflowStepException,
    
    # 空间配置异常
    SpatialConfigurationException,
    SpatialEntityException,
    SpatialHierarchyException,
    AccessControlException,
    
    # 业务规则异常
    BusinessRuleException,
    BusinessRuleConfigurationException,
    BusinessRuleExecutionException,
    RuleConditionException,
    RuleActionException,
    
    # 缓存异常
    CacheException
)

__all__ = [
    # 基础异常
    "ConfigurationException",
    "ValidationException",
    "ConfigurationNotFoundException", 
    "ConfigurationVersionException",
    "DuplicateConfigurationException",
    "PermissionDeniedException",
    
    # 表单配置异常
    "FormConfigurationException",
    "FormValidationException",
    "FormFieldException",
    "UnsupportedFieldTypeException",
    
    # 工作流配置异常
    "WorkflowException",
    "WorkflowConfigurationException",
    "WorkflowExecutionException",
    "WorkflowTimeoutException",
    "WorkflowStepException",
    
    # 空间配置异常
    "SpatialConfigurationException",
    "SpatialEntityException",
    "SpatialHierarchyException",
    "AccessControlException",
    
    # 业务规则异常
    "BusinessRuleException",
    "BusinessRuleConfigurationException",
    "BusinessRuleExecutionException",
    "RuleConditionException",
    "RuleActionException",
    
    # 缓存异常
    "CacheException"
] 