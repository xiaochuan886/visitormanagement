"""
配置引擎相关枚举定义
定义配置系统中使用的各种枚举类型
"""
from enum import Enum


class FormType(str, Enum):
    """表单类型枚举"""
    VISITOR_REGISTRATION = "visitor_registration"    # 访客注册表单
    APPROVAL_FORM = "approval_form"                  # 审批表单
    EMPLOYEE_FORM = "employee_form"                  # 员工表单
    SITE_FORM = "site_form"                         # 站点表单
    DEPARTMENT_FORM = "department_form"             # 部门表单
    CHECKIN_FORM = "checkin_form"                   # 签到表单
    CHECKOUT_FORM = "checkout_form"                 # 签出表单
    SURVEY_FORM = "survey_form"                     # 调查表单
    CUSTOM_FORM = "custom_form"                     # 自定义表单


class FieldType(str, Enum):
    """表单字段类型枚举"""
    TEXT = "text"                    # 文本输入框
    TEXTAREA = "textarea"            # 多行文本框
    SELECT = "select"                # 下拉选择框
    MULTISELECT = "multiselect"      # 多选下拉框
    RADIO = "radio"                  # 单选按钮
    CHECKBOX = "checkbox"            # 复选框
    DATE = "date"                    # 日期选择器
    DATETIME = "datetime"            # 日期时间选择器
    TIME = "time"                    # 时间选择器
    FILE = "file"                    # 文件上传
    NUMBER = "number"                # 数字输入框
    EMAIL = "email"                  # 邮箱输入框
    PHONE = "phone"                  # 电话号码输入框
    URL = "url"                      # URL输入框
    PASSWORD = "password"            # 密码输入框
    HIDDEN = "hidden"                # 隐藏字段
    SPATIAL_SELECTOR = "spatial_selector"  # 空间选择器
    EMPLOYEE_SELECTOR = "employee_selector"  # 员工选择器
    DEPARTMENT_SELECTOR = "department_selector"  # 部门选择器


class WorkflowType(str, Enum):
    """工作流类型枚举"""
    VISITOR_APPROVAL = "visitor_approval"        # 访客审批工作流
    DEVICE_CONTROL = "device_control"           # 设备控制工作流
    NOTIFICATION = "notification"               # 通知工作流
    DATA_SYNC = "data_sync"                    # 数据同步工作流
    SECURITY_CHECK = "security_check"          # 安全检查工作流
    ACCESS_CONTROL = "access_control"          # 访问控制工作流
    MAINTENANCE = "maintenance"                # 维护工作流
    EMERGENCY = "emergency"                    # 应急处理工作流


class WorkflowStatus(str, Enum):
    """工作流执行状态枚举"""
    PENDING = "pending"              # 待执行
    RUNNING = "running"              # 执行中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 执行失败
    CANCELLED = "cancelled"          # 已取消
    TIMEOUT = "timeout"              # 执行超时
    PAUSED = "paused"                # 已暂停


class StepType(str, Enum):
    """工作流步骤类型枚举"""
    MANUAL = "manual"                # 手动步骤
    AUTOMATIC = "automatic"          # 自动步骤
    CONDITIONAL = "conditional"      # 条件步骤
    PARALLEL = "parallel"            # 并行步骤
    NOTIFICATION = "notification"    # 通知步骤
    APPROVAL = "approval"            # 审批步骤
    SCRIPT = "script"                # 脚本执行步骤


class ApprovalType(str, Enum):
    """审批类型枚举"""
    SINGLE_APPROVER = "single_approver"      # 单人审批
    MULTIPLE_APPROVERS = "multiple_approvers"  # 多人审批
    ANY_APPROVER = "any_approver"            # 任一审批人
    ALL_APPROVERS = "all_approvers"          # 所有审批人
    ROLE_BASED = "role_based"                # 基于角色审批
    DEPARTMENT_HEAD = "department_head"      # 部门负责人审批
    SITE_MANAGER = "site_manager"           # 站点管理员审批


class BusinessRuleCategory(str, Enum):
    """业务规则类别枚举"""
    VALIDATION = "validation"        # 验证规则
    AUTOMATION = "automation"        # 自动化规则
    SECURITY = "security"           # 安全规则
    NOTIFICATION = "notification"    # 通知规则
    ACCESS_CONTROL = "access_control"  # 访问控制规则
    DATA_PROCESSING = "data_processing"  # 数据处理规则
    WORKFLOW_TRIGGER = "workflow_trigger"  # 工作流触发规则
    AUDIT = "audit"                 # 审计规则


class RuleExecutionResult(str, Enum):
    """规则执行结果枚举"""
    SUCCESS = "success"              # 执行成功
    FAILED = "failed"                # 执行失败
    SKIPPED = "skipped"              # 已跳过
    ERROR = "error"                  # 执行错误
    TIMEOUT = "timeout"              # 执行超时


class ConfigurationStatus(str, Enum):
    """配置状态枚举"""
    DRAFT = "draft"                  # 草稿状态
    ACTIVE = "active"                # 激活状态
    INACTIVE = "inactive"            # 停用状态
    DEPRECATED = "deprecated"        # 已弃用
    ARCHIVED = "archived"            # 已归档


class ValidationSeverity(str, Enum):
    """验证严重级别枚举"""
    INFO = "info"                    # 信息级别
    WARNING = "warning"              # 警告级别
    ERROR = "error"                  # 错误级别
    CRITICAL = "critical"            # 严重级别


class CacheStrategy(str, Enum):
    """缓存策略枚举"""
    NO_CACHE = "no_cache"            # 不缓存
    SHORT_TERM = "short_term"        # 短期缓存（5分钟）
    MEDIUM_TERM = "medium_term"      # 中期缓存（30分钟）
    LONG_TERM = "long_term"          # 长期缓存（2小时）
    PERSISTENT = "persistent"        # 持久缓存（直到手动清除）


class EventType(str, Enum):
    """配置事件类型枚举"""
    CONFIGURATION_CREATED = "configuration_created"
    CONFIGURATION_UPDATED = "configuration_updated"
    CONFIGURATION_DELETED = "configuration_deleted"
    CONFIGURATION_ACTIVATED = "configuration_activated"
    CONFIGURATION_DEACTIVATED = "configuration_deactivated"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    RULE_EXECUTED = "rule_executed"
    SPATIAL_ENTITY_CREATED = "spatial_entity_created"
    SPATIAL_ENTITY_UPDATED = "spatial_entity_updated" 