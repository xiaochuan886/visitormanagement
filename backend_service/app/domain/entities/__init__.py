"""
业务实体模块
"""

from .base import BaseEntity
from .visitor import Visitor
from .employee import Employee
from .department import Department
from .site import Site

__all__ = [
    "BaseEntity",
    "Visitor", 
    "Employee",
    "Department",
    "Site"
] 