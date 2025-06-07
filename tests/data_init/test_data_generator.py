"""
测试数据生成器
使用faker库生成真实的测试数据
"""
import random
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional

from faker import Faker
from faker.providers import internet, company, person, address, phone_number


class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self, locale: str = "zh_CN"):
        """
        初始化数据生成器
        
        Args:
            locale: 本地化设置
        """
        self.fake = Faker(locale)
        self.fake.add_provider(internet)
        self.fake.add_provider(company)
        self.fake.add_provider(person)
        self.fake.add_provider(address)
        self.fake.add_provider(phone_number)
        
        # 预定义的枚举值
        self.visitor_statuses = ["pending", "approved", "rejected", "checked_in", "checked_out", "cancelled", "expired"]
        self.approval_outcomes = ["pending", "approved", "rejected"]
        self.genders = ["male", "female", "other"]
        self.visit_purposes = ["business", "interview", "delivery", "maintenance", "meeting", "training", "other"]
        self.employee_statuses = ["active", "inactive", "suspended"]
        self.site_statuses = ["active", "inactive", "maintenance"]
    
    def generate_site_data(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        生成站点测试数据
        
        Args:
            count: 生成数量
            
        Returns:
            站点数据列表
        """
        sites = []
        
        for i in range(count):
            site = {
                "name": f"{self.fake.company()}办公区",
                "code": f"SITE{i+1:03d}",
                "address": self.fake.address(),
                "description": f"这是{self.fake.company()}的办公场所，位于{self.fake.city()}",
                "contact_person": self.fake.name(),
                "contact_phone": self.fake.phone_number(),
                "contact_email": self.fake.email(),
                "status": random.choice(self.site_statuses),
                "timezone": "Asia/Shanghai",
                "working_hours_start": "09:00",
                "working_hours_end": "18:00",
                "max_visitors_per_day": random.randint(50, 200),
                "require_approval": random.choice([True, False]),
                "allow_walk_in": random.choice([True, False])
            }
            sites.append(site)
        
        return sites
    
    def generate_department_data(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        生成部门测试数据
        
        Args:
            count: 生成数量
            
        Returns:
            部门数据列表
        """
        departments = []
        
        # 预定义的部门名称
        dept_names = [
            "人力资源部", "财务部", "技术部", "市场部", "销售部",
            "运营部", "产品部", "客服部", "法务部", "行政部"
        ]
        
        for i in range(count):
            dept_name = dept_names[i] if i < len(dept_names) else f"{self.fake.company()}部"
            
            department = {
                "name": dept_name,
                "code": f"DEPT{i+1:03d}",
                "description": f"{dept_name}负责{self.fake.catch_phrase()}相关工作",
                "manager_name": self.fake.name(),
                "manager_email": self.fake.email(),
                "manager_phone": self.fake.phone_number(),
                "location": f"{random.randint(1, 20)}楼{random.randint(1, 10)}层",
                "budget": random.randint(100000, 1000000),
                "employee_count": random.randint(5, 50),
                "parent_department_id": None if i < 2 else random.randint(1, 2)  # 前两个作为顶级部门
            }
            departments.append(department)
        
        return departments
    
    def generate_employee_data(self, count: int = 10, department_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        生成员工测试数据
        
        Args:
            count: 生成数量
            department_ids: 部门ID列表
            
        Returns:
            员工数据列表
        """
        employees = []
        
        if not department_ids:
            department_ids = list(range(1, 6))  # 默认使用1-5的部门ID
        
        for i in range(count):
            employee = {
                "employee_id": f"EMP{i+1:04d}",
                "name": self.fake.name(),
                "email": self.fake.email(),
                "phone_number": self.fake.phone_number(),
                "department_id": random.choice(department_ids),
                "position": random.choice([
                    "软件工程师", "产品经理", "设计师", "测试工程师", "运营专员",
                    "销售代表", "客服专员", "财务分析师", "人事专员", "行政助理"
                ]),
                "level": random.choice(["初级", "中级", "高级", "专家", "总监"]),
                "hire_date": self.fake.date_between(start_date="-5y", end_date="today"),
                "status": random.choice(self.employee_statuses),
                "manager_id": None if i < 3 else random.randint(1, 3),  # 前三个作为管理者
                "office_location": f"{random.randint(1, 20)}楼{random.randint(1, 10)}层{random.randint(1, 50)}号",
                "work_phone": self.fake.phone_number(),
                "emergency_contact": self.fake.name(),
                "emergency_phone": self.fake.phone_number()
            }
            employees.append(employee)
        
        return employees
    
    def generate_visitor_data(self, count: int = 20, employee_ids: List[int] = None, 
                            site_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        生成访客测试数据
        
        Args:
            count: 生成数量
            employee_ids: 员工ID列表
            site_ids: 站点ID列表
            
        Returns:
            访客数据列表
        """
        visitors = []
        
        if not employee_ids:
            employee_ids = list(range(1, 11))  # 默认使用1-10的员工ID
        
        if not site_ids:
            site_ids = list(range(1, 4))  # 默认使用1-3的站点ID
        
        for i in range(count):
            # 生成访问时间
            expected_date = self.fake.date_between(start_date="-30d", end_date="+30d")
            expected_time = time(
                hour=random.randint(9, 17),
                minute=random.choice([0, 15, 30, 45])
            )
            
            # 根据访问日期确定状态
            today = datetime.now().date()
            if expected_date < today:
                # 过去的访问，随机分配已完成的状态
                status = random.choice(["checked_out", "cancelled", "expired"])
            elif expected_date == today:
                # 今天的访问，可能正在进行
                status = random.choice(["approved", "checked_in", "checked_out"])
            else:
                # 未来的访问，待审批或已审批
                status = random.choice(["pending", "approved", "rejected"])
            
            visitor = {
                "name": self.fake.name(),
                "email": self.fake.email(),
                "phone_number": self.fake.phone_number(),
                "identification_no": self.fake.ssn(),
                "license_plate_number": self.fake.license_plate() if random.choice([True, False]) else None,
                "address": self.fake.address(),
                "gender": random.choice(self.genders),
                "company_name": self.fake.company(),
                "purpose": random.choice(self.visit_purposes),
                "comment": self.fake.text(max_nb_chars=200) if random.choice([True, False]) else None,
                "employee_id": random.choice(employee_ids),
                "expected_date": expected_date.isoformat(),
                "expected_time": expected_time.strftime("%H:%M:%S"),
                "privacy_policy": True,
                "promise": True,
                "site_id": random.choice(site_ids),
                "status": status,
                "approved": status in ["approved", "checked_in", "checked_out"],
                "approval_outcome": "approved" if status in ["approved", "checked_in", "checked_out"] else "pending",
                "approval_comment": self.fake.sentence() if status == "approved" else None
            }
            
            # 如果已签到，添加签到时间
            if status in ["checked_in", "checked_out"]:
                checkin_time = datetime.combine(expected_date, expected_time)
                visitor["checkin_date"] = checkin_time.isoformat()
            
            # 如果已签出，添加签出时间
            if status == "checked_out":
                checkout_time = checkin_time + timedelta(hours=random.randint(1, 8))
                visitor["checkout_date"] = checkout_time.isoformat()
            
            visitors.append(visitor)
        
        return visitors
    
    def generate_test_users(self) -> List[Dict[str, Any]]:
        """
        生成测试用户数据
        
        Returns:
            测试用户列表
        """
        users = [
            {
                "username": "admin",
                "password": "admin123",
                "email": "admin@example.com",
                "name": "系统管理员",
                "roles": ["admin"],
                "permissions": ["visitor:read", "visitor:write", "visitor:delete"],
                "tenant_id": "default"
            },
            {
                "username": "manager",
                "password": "manager123",
                "email": "manager@example.com",
                "name": "部门经理",
                "roles": ["manager"],
                "permissions": ["visitor:read", "visitor:write"],
                "tenant_id": "default"
            },
            {
                "username": "employee",
                "password": "employee123",
                "email": "employee@example.com",
                "name": "普通员工",
                "roles": ["employee"],
                "permissions": ["visitor:read"],
                "tenant_id": "default"
            }
        ]
        
        return users
    
    def generate_complete_test_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        生成完整的测试数据集
        
        Returns:
            包含所有测试数据的字典
        """
        # 生成基础数据
        sites = self.generate_site_data(3)
        departments = self.generate_department_data(5)
        employees = self.generate_employee_data(10, list(range(1, 6)))
        visitors = self.generate_visitor_data(20, list(range(1, 11)), list(range(1, 4)))
        users = self.generate_test_users()
        
        return {
            "sites": sites,
            "departments": departments,
            "employees": employees,
            "visitors": visitors,
            "users": users
        }
    
    def generate_visitor_for_status(self, status: str, employee_id: int = 1, 
                                  site_id: int = 1) -> Dict[str, Any]:
        """
        生成特定状态的访客数据
        
        Args:
            status: 访客状态
            employee_id: 员工ID
            site_id: 站点ID
            
        Returns:
            访客数据
        """
        # 根据状态调整时间
        if status in ["checked_out", "cancelled", "expired"]:
            expected_date = (datetime.now() - timedelta(days=random.randint(1, 7))).date()
        elif status in ["checked_in"]:
            expected_date = datetime.now().date()
        else:
            expected_date = (datetime.now() + timedelta(days=random.randint(1, 7))).date()
        
        expected_time = time(
            hour=random.randint(9, 17),
            minute=random.choice([0, 15, 30, 45])
        )
        
        # 组合日期和时间为完整的datetime
        expected_datetime = datetime.combine(expected_date, expected_time)
        
        visitor = {
            "name": self.fake.name(),
            "email": self.fake.email(),
            "phone_number": self.fake.phone_number(),
            "identification_no": self.fake.ssn(),
            "company_name": self.fake.company(),
            "purpose": random.choice(self.visit_purposes),
            "employee_id": employee_id,
            "expected_date": expected_datetime.isoformat(),  # 使用完整的ISO格式
            "expected_time": expected_time.strftime("%H:%M:%S"),
            "privacy_policy": True,
            "promise": True,
            "site_id": site_id
        }
        
        return visitor 