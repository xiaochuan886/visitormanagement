"""
SQLAlchemy数据库模型定义
"""
from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .connection import Base


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
    status = Column(String(20), default="pending")
    approved = Column(Boolean)
    approval_outcome = Column(String(20))
    approval_comment = Column(Text)
    
    # 关联信息
    site_id = Column(Integer, ForeignKey("sites.id"))
    survey_response_value = Column(Integer)
    
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