"""
SQLAlchemy数据库模型定义
优化版本 v2.0 - 支持枚举类型、约束和性能优化
"""
from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Time, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

from .connection import Base

# 定义枚举类型
visitor_status_enum = ENUM(
    'pending', 'approved', 'rejected', 'checked_in', 
    'checked_out', 'cancelled', 'expired',
    name='visitor_status'
)

approval_action_enum = ENUM(
    'approve', 'reject', 'modify', 'cancel',
    name='approval_action'
)


class BaseModel:
    """模型基类"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditableModel(BaseModel):
    """可审计模型基类"""
    created_by = Column(String(100))
    updated_by = Column(String(100))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(String(100))


class TenantModel(AuditableModel):
    """多租户模型基类"""
    tenant_id = Column(String(50), default="default", index=True)


class SiteModel(Base, TenantModel):
    """站点模型"""
    __tablename__ = "sites"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    address = Column(String(200))
    city = Column(String(50))
    province = Column(String(50))
    postal_code = Column(String(10))
    country = Column(String(50), default="中国")
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(20), default="active")
    working_hours_start = Column(String(5), default="09:00")
    working_hours_end = Column(String(5), default="18:00")
    timezone = Column(String(50), default="Asia/Shanghai")
    
    # 约束
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'maintenance')", name='chk_sites_status'),
        CheckConstraint("email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_sites_email'),
    )


class DepartmentModel(Base, TenantModel):
    """部门模型"""
    __tablename__ = "departments"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50))
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    sort_order = Column(Integer, default=0)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    site_id = Column(Integer, ForeignKey("sites.id"))
    
    # 约束
    __table_args__ = (
        CheckConstraint("email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_departments_email'),
        CheckConstraint("parent_id != id", name='chk_departments_no_self_parent'),
    )
    
    # 关系
    parent = relationship("DepartmentModel", remote_side=lambda: DepartmentModel.id)
    children = relationship("DepartmentModel", back_populates="parent")
    site = relationship("SiteModel")
    manager = relationship("EmployeeModel", foreign_keys=[manager_id])


class DesignationModel(Base, TenantModel):
    """职位模型"""
    __tablename__ = "designations"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50))
    description = Column(Text)
    level = Column(Integer, default=1)
    site_id = Column(Integer, ForeignKey("sites.id"))
    
    # 约束
    __table_args__ = (
        CheckConstraint("level >= 1 AND level <= 10", name='chk_designations_level'),
    )
    
    # 关系
    site = relationship("SiteModel")


class EmployeeModel(Base, TenantModel):
    """员工模型"""
    __tablename__ = "employees"
    
    # 基本信息
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), nullable=False, unique=True)  # 员工工号
    email = Column(String(100))
    phone_number = Column(String(20))
    gender = Column(String(10))
    
    # 组织信息
    department_id = Column(Integer, ForeignKey("departments.id"))
    designation_id = Column(Integer, ForeignKey("designations.id"))
    position = Column(String(100))  # 职位名称
    manager_id = Column(Integer, ForeignKey("employees.id"))  # 上级员工ID
    
    # 个人信息
    about = Column(Text)
    avatar = Column(String(200))
    employee_number = Column(String(50))  # 保留原字段兼容性
    hire_date = Column(DateTime(timezone=True))  # 入职日期
    birth_date = Column(DateTime(timezone=True))  # 出生日期
    address = Column(String(200))  # 地址
    
    # 紧急联系人
    emergency_contact = Column(String(100))  # 紧急联系人
    emergency_phone = Column(String(20))  # 紧急联系电话
    
    # 薪资信息
    salary = Column(Float)  # 薪资
    
    # 状态信息
    status = Column(String(20), default="active")
    related_account_id = Column(String(100))
    site_id = Column(Integer, ForeignKey("sites.id"))
    
    # 约束
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'terminated', 'on_leave')", name='chk_employees_status'),
        CheckConstraint("email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_employees_email'),
        CheckConstraint("gender IS NULL OR gender IN ('male', 'female', 'other')", name='chk_employees_gender'),
        CheckConstraint("manager_id != id", name='chk_employees_no_self_manager'),
        CheckConstraint("salary IS NULL OR salary >= 0", name='chk_employees_salary'),
    )
    
    # 关系
    department = relationship("DepartmentModel", foreign_keys=[department_id])
    designation = relationship("DesignationModel")
    site = relationship("SiteModel")
    manager = relationship("EmployeeModel", remote_side=lambda: EmployeeModel.id)  # 上级员工关系


class VisitorModel(Base, TenantModel):
    """访客模型"""
    __tablename__ = "visitors"
    
    # 基本信息
    pass_code = Column(String(50))
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone_number = Column(String(20))
    identification_no = Column(String(50))
    license_plate_number = Column(String(20))
    address = Column(String(200))
    gender = Column(String(10))
    company_name = Column(String(100))
    
    # 访问信息
    purpose = Column(String(50))
    comment = Column(Text)
    designation_id = Column(Integer, ForeignKey("designations.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    
    # 时间信息
    checkin_date = Column(DateTime(timezone=True))
    checkout_date = Column(DateTime(timezone=True))
    expected_date = Column(DateTime(timezone=True))
    expected_time = Column(Time)
    
    # 附加信息
    avatar = Column(String(200))
    trip_code = Column(String(100))
    health_code = Column(String(100))
    qr_code = Column(String(200))
    nucleic_acid_test_report = Column(String(200))
    
    # 协议和承诺
    privacy_policy = Column(Boolean)
    promise = Column(Boolean)
    
    # 状态信息
    status = Column(visitor_status_enum, default='pending')
    approved = Column(Boolean)
    approval_outcome = Column(String(20))
    approval_comment = Column(Text)
    
    # 关联信息
    site_id = Column(Integer, ForeignKey("sites.id"))
    survey_response_value = Column(Integer)
    
    # 约束
    __table_args__ = (
        CheckConstraint("checkout_date IS NULL OR checkin_date IS NULL OR checkout_date > checkin_date", name='chk_visitors_checkout_after_checkin'),
        CheckConstraint("email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name='chk_visitors_email'),
        CheckConstraint("gender IS NULL OR gender IN ('male', 'female', 'other')", name='chk_visitors_gender'),
        CheckConstraint("survey_response_value IS NULL OR (survey_response_value >= 1 AND survey_response_value <= 10)", name='chk_visitors_survey_score'),
    )
    
    # 关系
    designation = relationship("DesignationModel")
    employee = relationship("EmployeeModel")
    site = relationship("SiteModel")


class VisitorHistoryModel(Base, TenantModel):
    """访客历史模型"""
    __tablename__ = "visitor_histories"
    
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    action = Column(String(50), nullable=False)
    action_time = Column(DateTime(timezone=True), default=func.now())
    description = Column(Text)
    operator = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # 关系
    visitor = relationship("VisitorModel")


class ApprovalHistoryModel(Base, TenantModel):
    """审批历史模型"""
    __tablename__ = "approval_histories"
    
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("employees.id"))
    approval_outcome = Column(String(20), nullable=False)
    approval_comment = Column(Text)
    approval_date = Column(DateTime(timezone=True), default=func.now())
    
    # 关系
    visitor = relationship("VisitorModel")
    approver = relationship("EmployeeModel")


class CheckinPointModel(Base, TenantModel):
    """签到点模型"""
    __tablename__ = "checkin_points"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    
    # 关系
    site = relationship("SiteModel")


class CompanionModel(Base, TenantModel):
    """同行人员模型"""
    __tablename__ = "companions"
    
    visitor_id = Column(Integer, ForeignKey("visitors.id"), nullable=False)
    name = Column(String(100), nullable=False)
    identification_no = Column(String(50))
    phone_number = Column(String(20))
    relationship_type = Column(String(50))
    
    # 关系
    visitor = relationship("VisitorModel")


# ===== 配置引擎数据模型 =====

class FormConfigurationModel(Base, TenantModel):
    """表单配置模型"""
    __tablename__ = "form_configurations"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    form_type = Column(String(50), nullable=False)
    form_name = Column(String(100), nullable=False)
    form_version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    description = Column(Text)
    form_schema = Column(postgresql.JSONB)      # 完整表单结构
    ui_schema = Column(postgresql.JSONB)        # UI渲染配置
    validation_schema = Column(postgresql.JSONB)  # 验证规则
    
    # 约束
    __table_args__ = (
        CheckConstraint("form_type IN ('visitor_registration', 'approval_form', 'employee_form', 'site_form', 'department_form')", name='chk_form_type'),
        CheckConstraint("form_version >= 1", name='chk_form_version'),
    )
    
    # 关系
    form_fields = relationship("FormFieldConfigurationModel", back_populates="form_config", cascade="all, delete-orphan")


class FormFieldConfigurationModel(Base):
    """表单字段配置模型"""
    __tablename__ = "form_field_configurations"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    form_config_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('form_configurations.id', ondelete='CASCADE'), nullable=False)
    field_key = Column(String(100), nullable=False)
    field_label = Column(String(200), nullable=False)
    field_type = Column(String(50), nullable=False)
    field_order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    is_readonly = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    validation_rules = Column(postgresql.JSONB)
    field_options = Column(postgresql.JSONB)
    conditional_logic = Column(postgresql.JSONB)
    default_value = Column(Text)
    placeholder_text = Column(String(200))
    help_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint("field_type IN ('text', 'textarea', 'select', 'multiselect', 'radio', 'checkbox', 'date', 'datetime', 'time', 'file', 'number', 'email', 'phone', 'url')", name='chk_field_type'),
        CheckConstraint("field_order >= 0", name='chk_field_order'),
    )
    
    # 关系
    form_config = relationship("FormConfigurationModel", back_populates="form_fields")


class SpatialConfigurationModel(Base, TenantModel):
    """空间配置模型"""
    __tablename__ = "spatial_configurations"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    config_name = Column(String(100), nullable=False)
    spatial_levels = Column(postgresql.JSONB, nullable=False)          # ["site", "building", "floor", "zone", "room"]
    level_settings = Column(postgresql.JSONB, nullable=False)          # 各层级的设置
    access_control_settings = Column(postgresql.JSONB)                 # 访问控制配置
    device_integration_settings = Column(postgresql.JSONB)             # 设备集成配置
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # 关系
    spatial_entities = relationship("SpatialEntityModel", back_populates="spatial_config", cascade="all, delete-orphan")


class SpatialEntityModel(Base, TenantModel):
    """空间实体模型"""
    __tablename__ = "spatial_entities"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    spatial_config_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('spatial_configurations.id', ondelete='CASCADE'), nullable=False)
    entity_type = Column(String(50), nullable=False)          # site, building, floor, zone, room
    entity_level = Column(Integer, nullable=False)            # 0=site, 1=building, 2=floor, etc.
    parent_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('spatial_entities.id', ondelete='CASCADE'))
    entity_code = Column(String(100), nullable=False)
    entity_name = Column(String(200), nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    entity_attributes = Column(postgresql.JSONB)              # 自定义属性
    access_control_rules = Column(postgresql.JSONB)           # 访问控制规则
    device_integrations = Column(postgresql.JSONB)            # 设备集成配置
    location_data = Column(postgresql.JSONB)                  # 位置信息（经纬度、楼层图等）
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint("entity_type IN ('site', 'building', 'floor', 'zone', 'room', 'area', 'workstation')", name='chk_entity_type'),
        CheckConstraint("entity_level >= 0 AND entity_level <= 10", name='chk_entity_level'),
        CheckConstraint("display_order >= 0", name='chk_display_order'),
    )
    
    # 关系
    spatial_config = relationship("SpatialConfigurationModel", back_populates="spatial_entities")
    parent = relationship("SpatialEntityModel", remote_side=lambda: SpatialEntityModel.id)
    children = relationship("SpatialEntityModel", back_populates="parent")


class WorkflowConfigurationModel(Base, TenantModel):
    """工作流配置模型"""
    __tablename__ = "workflow_configurations"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    workflow_name = Column(String(100), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    workflow_version = Column(Integer, default=1, nullable=False)
    trigger_conditions = Column(postgresql.JSONB, nullable=False)       # 触发条件
    workflow_steps = Column(postgresql.JSONB, nullable=False)           # 工作流步骤定义
    failure_handling = Column(postgresql.JSONB)                         # 失败处理策略
    timeout_settings = Column(postgresql.JSONB)                         # 超时设置
    is_active = Column(Boolean, default=True, nullable=False)
    priority_level = Column(Integer, default=1, nullable=False)
    description = Column(Text)
    
    # 约束
    __table_args__ = (
        CheckConstraint("workflow_type IN ('visitor_approval', 'device_control', 'notification', 'data_sync', 'security_check')", name='chk_workflow_type'),
        CheckConstraint("workflow_version >= 1", name='chk_workflow_version'),
        CheckConstraint("priority_level >= 1 AND priority_level <= 10", name='chk_priority_level'),
    )
    
    # 关系
    workflow_executions = relationship("WorkflowExecutionModel", back_populates="workflow_config")


class WorkflowExecutionModel(Base, TenantModel):
    """工作流执行模型"""
    __tablename__ = "workflow_executions"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    workflow_config_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('workflow_configurations.id'), nullable=False)
    target_entity_type = Column(String(50), nullable=False)             # visitor, employee, etc.
    target_entity_id = Column(String(100), nullable=False)
    execution_status = Column(String(50), nullable=False)              # pending, running, completed, failed, cancelled
    current_step = Column(Integer, default=0, nullable=False)
    execution_data = Column(postgresql.JSONB)                          # 执行过程数据
    step_results = Column(postgresql.JSONB)                            # 各步骤执行结果
    context_data = Column(postgresql.JSONB)                            # 上下文数据
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    last_executed_at = Column(DateTime(timezone=True))
    error_details = Column(Text)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint("execution_status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')", name='chk_execution_status'),
        CheckConstraint("current_step >= 0", name='chk_current_step'),
        CheckConstraint("retry_count >= 0", name='chk_retry_count'),
    )
    
    # 关系
    workflow_config = relationship("WorkflowConfigurationModel", back_populates="workflow_executions")


class BusinessRuleModel(Base, TenantModel):
    """业务规则模型"""
    __tablename__ = "business_rules"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    rule_name = Column(String(100), nullable=False)
    rule_category = Column(String(50), nullable=False)
    rule_version = Column(Integer, default=1, nullable=False)
    rule_conditions = Column(postgresql.JSONB, nullable=False)          # 规则条件
    rule_actions = Column(postgresql.JSONB, nullable=False)             # 规则动作
    rule_priority = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    effective_from = Column(DateTime(timezone=True))
    effective_until = Column(DateTime(timezone=True))
    description = Column(Text)
    
    # 约束
    __table_args__ = (
        CheckConstraint("rule_category IN ('validation', 'automation', 'security', 'notification', 'access_control', 'data_processing')", name='chk_rule_category'),
        CheckConstraint("rule_version >= 1", name='chk_rule_version'),
        CheckConstraint("rule_priority >= 1 AND rule_priority <= 100", name='chk_rule_priority'),
        CheckConstraint("effective_until IS NULL OR effective_until > effective_from", name='chk_rule_effective_dates'),
    )
    
    # 关系
    rule_execution_logs = relationship("RuleExecutionLogModel", back_populates="business_rule")


class RuleExecutionLogModel(Base, TenantModel):
    """规则执行日志模型"""
    __tablename__ = "rule_execution_logs"
    
    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    rule_id = Column(postgresql.UUID(as_uuid=True), ForeignKey('business_rules.id'), nullable=False)
    target_entity_type = Column(String(50), nullable=False)
    target_entity_id = Column(String(100), nullable=False)
    execution_result = Column(String(50), nullable=False)              # success, failed, skipped, error
    execution_details = Column(postgresql.JSONB)
    input_data = Column(postgresql.JSONB)                              # 输入数据
    output_data = Column(postgresql.JSONB)                             # 输出数据
    execution_time_ms = Column(Integer)                                # 执行时间（毫秒）
    error_message = Column(Text)
    execution_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 约束
    __table_args__ = (
        CheckConstraint("execution_result IN ('success', 'failed', 'skipped', 'error', 'timeout')", name='chk_execution_result'),
        CheckConstraint("execution_time_ms IS NULL OR execution_time_ms >= 0", name='chk_execution_time_ms'),
    )
    
    # 关系
    business_rule = relationship("BusinessRuleModel", back_populates="rule_execution_logs")


# 为向后兼容和服务使用提供的别名
Visitor = VisitorModel
Site = SiteModel
Department = DepartmentModel
Designation = DesignationModel
Employee = EmployeeModel
VisitorHistory = VisitorHistoryModel
ApprovalHistory = ApprovalHistoryModel
CheckinPoint = CheckinPointModel
Companion = CompanionModel

# 配置引擎模型别名
FormConfiguration = FormConfigurationModel
FormFieldConfiguration = FormFieldConfigurationModel
SpatialConfiguration = SpatialConfigurationModel
SpatialEntity = SpatialEntityModel
WorkflowConfiguration = WorkflowConfigurationModel
WorkflowExecution = WorkflowExecutionModel
BusinessRule = BusinessRuleModel
RuleExecutionLog = RuleExecutionLogModel 