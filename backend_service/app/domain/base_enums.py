"""
领域层枚举定义
定义系统中使用的各种枚举类型
"""
from enum import Enum


class VisitorStatus(str, Enum):
    """访客状态枚举"""
    PENDING = "pending"           # 待审批
    APPROVED = "approved"         # 已审批
    REJECTED = "rejected"         # 已拒绝
    CHECKED_IN = "checked_in"     # 已签到
    CHECKED_OUT = "checked_out"   # 已签出
    CANCELLED = "cancelled"       # 已取消
    EXPIRED = "expired"           # 已过期


class ApprovalOutcome(str, Enum):
    """审批结果枚举"""
    PENDING = "pending"    # 待审批
    APPROVED = "approved"  # 通过
    REJECTED = "rejected"  # 拒绝


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"      # 男性
    FEMALE = "female"  # 女性
    OTHER = "other"    # 其他


class DocumentType(str, Enum):
    """证件类型枚举"""
    ID_CARD = "id_card"              # 身份证
    PASSPORT = "passport"            # 护照
    DRIVER_LICENSE = "driver_license" # 驾驶证
    OTHER = "other"                  # 其他


class NotificationType(str, Enum):
    """通知类型枚举"""
    EMAIL = "email"    # 邮件
    SMS = "sms"        # 短信
    SYSTEM = "system"  # 系统通知


class EmployeeStatus(str, Enum):
    """员工状态枚举"""
    ACTIVE = "active"      # 在职
    INACTIVE = "inactive"  # 离职
    SUSPENDED = "suspended" # 停职


class SiteStatus(str, Enum):
    """站点状态枚举"""
    ACTIVE = "active"      # 启用
    INACTIVE = "inactive"  # 停用
    MAINTENANCE = "maintenance" # 维护中


class VisitPurpose(str, Enum):
    """访问目的枚举"""
    BUSINESS = "business"      # 商务会谈
    INTERVIEW = "interview"    # 面试
    DELIVERY = "delivery"      # 送货
    MAINTENANCE = "maintenance" # 维修
    MEETING = "meeting"        # 会议
    TRAINING = "training"      # 培训
    OTHER = "other"           # 其他 