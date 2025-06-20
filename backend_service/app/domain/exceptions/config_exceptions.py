"""
配置引擎相关异常定义
定义配置系统中使用的各种异常类型
"""
from typing import Dict, Any, Optional, List


class ConfigurationException(Exception):
    """配置引擎基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or "CONFIGURATION_ERROR"
        self.details = details or {}
        super().__init__(message)


class ValidationException(ConfigurationException):
    """验证异常基类"""
    
    def __init__(
        self,
        message: str,
        field_errors: Dict[str, List[str]] = None,
        error_code: str = None
    ):
        self.field_errors = field_errors or {}
        super().__init__(
            message,
            error_code or "VALIDATION_ERROR",
            {"field_errors": self.field_errors}
        )


class FormConfigurationException(ConfigurationException):
    """表单配置异常"""
    pass


class FormValidationException(FormConfigurationException):
    """表单验证异常"""
    
    def __init__(
        self,
        message: str,
        invalid_fields: List[str] = None,
        validation_errors: Dict[str, str] = None
    ):
        self.invalid_fields = invalid_fields or []
        self.validation_errors = validation_errors or {}
        super().__init__(
            message,
            "FORM_VALIDATION_ERROR",
            {
                "invalid_fields": self.invalid_fields,
                "validation_errors": self.validation_errors
            }
        )


class FormFieldException(FormConfigurationException):
    """表单字段异常"""
    
    def __init__(
        self,
        message: str,
        field_name: str,
        field_type: str = None
    ):
        self.field_name = field_name
        self.field_type = field_type
        super().__init__(
            message,
            "FORM_FIELD_ERROR",
            {
                "field_name": field_name,
                "field_type": field_type
            }
        )


class UnsupportedFieldTypeException(FormFieldException):
    """不支持的字段类型异常"""
    
    def __init__(self, field_type: str, field_name: str = None):
        super().__init__(
            f"不支持的字段类型: {field_type}",
            field_name or "unknown",
            field_type
        )
        self.error_code = "UNSUPPORTED_FIELD_TYPE"


class WorkflowException(ConfigurationException):
    """工作流异常基类"""
    pass


class WorkflowConfigurationException(WorkflowException):
    """工作流配置异常"""
    
    def __init__(
        self,
        message: str,
        workflow_id: str = None,
        workflow_type: str = None
    ):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        super().__init__(
            message,
            "WORKFLOW_CONFIGURATION_ERROR",
            {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type
            }
        )


class WorkflowExecutionException(WorkflowException):
    """工作流执行异常"""
    
    def __init__(
        self,
        message: str,
        workflow_id: str = None,
        step_name: str = None,
        execution_id: str = None
    ):
        self.workflow_id = workflow_id
        self.step_name = step_name
        self.execution_id = execution_id
        super().__init__(
            message,
            "WORKFLOW_EXECUTION_ERROR",
            {
                "workflow_id": workflow_id,
                "step_name": step_name,
                "execution_id": execution_id
            }
        )


class WorkflowTimeoutException(WorkflowExecutionException):
    """工作流超时异常"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        workflow_id: str = None,
        step_name: str = None
    ):
        self.timeout_seconds = timeout_seconds
        super().__init__(message, workflow_id, step_name)
        self.error_code = "WORKFLOW_TIMEOUT"
        self.details["timeout_seconds"] = timeout_seconds


class WorkflowStepException(WorkflowExecutionException):
    """工作流步骤异常"""
    
    def __init__(
        self,
        message: str,
        step_name: str,
        step_type: str = None,
        step_error: str = None
    ):
        self.step_type = step_type
        self.step_error = step_error
        super().__init__(message, step_name=step_name)
        self.error_code = "WORKFLOW_STEP_ERROR"
        self.details.update({
            "step_type": step_type,
            "step_error": step_error
        })


class SpatialConfigurationException(ConfigurationException):
    """空间配置异常"""
    pass


class SpatialEntityException(SpatialConfigurationException):
    """空间实体异常"""
    
    def __init__(
        self,
        message: str,
        entity_id: str = None,
        entity_type: str = None,
        entity_code: str = None
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.entity_code = entity_code
        super().__init__(
            message,
            "SPATIAL_ENTITY_ERROR",
            {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "entity_code": entity_code
            }
        )


class SpatialHierarchyException(SpatialConfigurationException):
    """空间层级异常"""
    
    def __init__(
        self,
        message: str,
        parent_id: str = None,
        child_id: str = None,
        hierarchy_level: int = None
    ):
        self.parent_id = parent_id
        self.child_id = child_id
        self.hierarchy_level = hierarchy_level
        super().__init__(
            message,
            "SPATIAL_HIERARCHY_ERROR",
            {
                "parent_id": parent_id,
                "child_id": child_id,
                "hierarchy_level": hierarchy_level
            }
        )


class AccessControlException(SpatialConfigurationException):
    """访问控制异常"""
    
    def __init__(
        self,
        message: str,
        entity_id: str = None,
        user_id: str = None,
        access_level: str = None
    ):
        self.entity_id = entity_id
        self.user_id = user_id
        self.access_level = access_level
        super().__init__(
            message,
            "ACCESS_CONTROL_ERROR",
            {
                "entity_id": entity_id,
                "user_id": user_id,
                "access_level": access_level
            }
        )


class BusinessRuleException(ConfigurationException):
    """业务规则异常基类"""
    pass


class BusinessRuleConfigurationException(BusinessRuleException):
    """业务规则配置异常"""
    
    def __init__(
        self,
        message: str,
        rule_id: str = None,
        rule_name: str = None,
        rule_category: str = None
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.rule_category = rule_category
        super().__init__(
            message,
            "BUSINESS_RULE_CONFIGURATION_ERROR",
            {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "rule_category": rule_category
            }
        )


class BusinessRuleExecutionException(BusinessRuleException):
    """业务规则执行异常"""
    
    def __init__(
        self,
        message: str,
        rule_id: str = None,
        execution_context: Dict[str, Any] = None,
        input_data: Dict[str, Any] = None
    ):
        self.rule_id = rule_id
        self.execution_context = execution_context or {}
        self.input_data = input_data or {}
        super().__init__(
            message,
            "BUSINESS_RULE_EXECUTION_ERROR",
            {
                "rule_id": rule_id,
                "execution_context": execution_context,
                "input_data": input_data
            }
        )


class RuleConditionException(BusinessRuleExecutionException):
    """规则条件异常"""
    
    def __init__(
        self,
        message: str,
        condition: Dict[str, Any],
        rule_id: str = None
    ):
        self.condition = condition
        super().__init__(message, rule_id)
        self.error_code = "RULE_CONDITION_ERROR"
        self.details["condition"] = condition


class RuleActionException(BusinessRuleExecutionException):
    """规则动作异常"""
    
    def __init__(
        self,
        message: str,
        action: Dict[str, Any],
        rule_id: str = None
    ):
        self.action = action
        super().__init__(message, rule_id)
        self.error_code = "RULE_ACTION_ERROR"
        self.details["action"] = action


class CacheException(ConfigurationException):
    """缓存异常"""
    
    def __init__(
        self,
        message: str,
        cache_key: str = None,
        operation: str = None
    ):
        self.cache_key = cache_key
        self.operation = operation
        super().__init__(
            message,
            "CACHE_ERROR",
            {
                "cache_key": cache_key,
                "operation": operation
            }
        )


class ConfigurationNotFoundException(ConfigurationException):
    """配置未找到异常"""
    
    def __init__(
        self,
        config_type: str,
        config_id: str = None,
        config_name: str = None
    ):
        self.config_type = config_type
        self.config_id = config_id
        self.config_name = config_name
        
        message = f"配置未找到: {config_type}"
        if config_id:
            message += f" (ID: {config_id})"
        if config_name:
            message += f" (名称: {config_name})"
            
        super().__init__(
            message,
            "CONFIGURATION_NOT_FOUND",
            {
                "config_type": config_type,
                "config_id": config_id,
                "config_name": config_name
            }
        )


class ConfigurationVersionException(ConfigurationException):
    """配置版本异常"""
    
    def __init__(
        self,
        message: str,
        config_id: str = None,
        version: int = None
    ):
        self.config_id = config_id
        self.version = version
        super().__init__(
            message,
            "CONFIGURATION_VERSION_ERROR",
            {
                "config_id": config_id,
                "version": version
            }
        )


class DuplicateConfigurationException(ConfigurationException):
    """重复配置异常"""
    
    def __init__(
        self,
        config_type: str,
        identifier: str,
        identifier_type: str = "name"
    ):
        self.config_type = config_type
        self.identifier = identifier
        self.identifier_type = identifier_type
        
        message = f"配置已存在: {config_type} ({identifier_type}: {identifier})"
        
        super().__init__(
            message,
            "DUPLICATE_CONFIGURATION",
            {
                "config_type": config_type,
                "identifier": identifier,
                "identifier_type": identifier_type
            }
        )


class PermissionDeniedException(ConfigurationException):
    """权限拒绝异常"""
    
    def __init__(
        self,
        message: str,
        user_id: str = None,
        required_permission: str = None,
        resource_type: str = None,
        resource_id: str = None
    ):
        self.user_id = user_id
        self.required_permission = required_permission
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message,
            "PERMISSION_DENIED",
            {
                "user_id": user_id,
                "required_permission": required_permission,
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


# ==================== 异常别名定义 ====================
# 为了兼容现有代码，提供常用的异常类别名

# 配置相关异常别名
ConfigurationNotFoundError = ConfigurationNotFoundException
ConfigurationValidationError = ValidationException
ValidationError = ValidationException  # 通用验证异常别名
ConfigurationConflictError = DuplicateConfigurationException

# 表单相关异常别名
FormConfigurationNotFoundError = FormConfigurationException
FormValidationError = FormValidationException

# 工作流相关异常别名
WorkflowConfigurationError = WorkflowConfigurationException
WorkflowExecutionError = WorkflowExecutionException
WorkflowStepError = WorkflowStepException

# 业务规则相关异常别名
BusinessRuleConfigurationError = BusinessRuleConfigurationException
BusinessRuleExecutionError = BusinessRuleExecutionException

# 空间配置相关异常别名
SpatialConfigurationError = SpatialConfigurationException
SpatialEntityError = SpatialEntityException
AccessControlError = AccessControlException 