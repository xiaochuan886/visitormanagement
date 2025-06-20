"""
创建访客管理系统基础测试数据
"""
import asyncio
import sys
import os
from datetime import datetime, date

sys.path.append('.')

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import SiteModel, DepartmentModel, EmployeeModel
from app.domain.base_enums import EmployeeStatus
from sqlalchemy import text, select, func


async def create_test_data():
    """创建基础测试数据"""
    print('🚀 创建访客管理系统基础测试数据')
    print('=' * 50)
    
    async for db in get_db():
        try:
            # 检查是否已有数据
            existing_sites = await db.execute(select(func.count(SiteModel.id)))
            site_count = existing_sites.scalar()
            
            if site_count > 0:
                print('⚠️  检测到已有站点数据，跳过创建')
                return
            
            tenant_id = "default_tenant"
            created_by = "system_init"
            
            # 1. 创建测试站点
            print('🏭 创建测试站点...')
            sites_data = [
                {
                    "name": "总部大厦",
                    "code": "HQ001",
                    "address": "上海市浦东新区世纪大道100号",
                    "description": "公司总部办公楼",
                    "phone": "021-12345678",
                    "email": "hq@company.com",
                    "city": "上海",
                    "province": "上海",
                    "postal_code": "200120"
                },
                {
                    "name": "研发中心", 
                    "code": "RD001",
                    "address": "上海市浦东新区张江高科技园区",
                    "description": "技术研发中心",
                    "phone": "021-87654321",
                    "email": "rd@company.com",
                    "city": "上海",
                    "province": "上海",
                    "postal_code": "201203"
                }
            ]
            
            sites = []
            for site_data in sites_data:
                site = SiteModel(
                    name=site_data["name"],
                    code=site_data["code"],
                    address=site_data["address"],
                    description=site_data["description"],
                    phone=site_data["phone"],
                    email=site_data["email"],
                    city=site_data["city"],
                    province=site_data["province"],
                    postal_code=site_data["postal_code"],
                    tenant_id=tenant_id,
                    created_by=created_by
                )
                db.add(site)
                sites.append(site)
            
            await db.flush()  # 获取ID
            print(f'✅ 创建了{len(sites)}个站点')
            
            # 2. 创建测试部门
            print('🏢 创建测试部门...')
            departments_data = [
                {
                    "name": "技术部",
                    "code": "TECH",
                    "description": "负责产品技术研发",
                    "site_id": sites[0].id
                },
                {
                    "name": "市场部",
                    "code": "MKT",
                    "description": "负责市场营销推广",
                    "site_id": sites[0].id
                },
                {
                    "name": "人事部",
                    "code": "HR",
                    "description": "负责人力资源管理",
                    "site_id": sites[0].id
                },
                {
                    "name": "研发一部",
                    "code": "RD1",
                    "description": "前端技术研发",
                    "site_id": sites[1].id
                },
                {
                    "name": "研发二部",
                    "code": "RD2",
                    "description": "后端技术研发",
                    "site_id": sites[1].id
                }
            ]
            
            departments = []
            for dept_data in departments_data:
                department = DepartmentModel(
                    name=dept_data["name"],
                    code=dept_data["code"],
                    description=dept_data["description"],
                    site_id=dept_data["site_id"],
                    tenant_id=tenant_id,
                    created_by=created_by
                )
                db.add(department)
                departments.append(department)
            
            await db.flush()  # 获取ID
            print(f'✅ 创建了{len(departments)}个部门')
            
            # 3. 创建测试员工
            print('👥 创建测试员工...')
            employees_data = [
                {
                    "name": "张三",
                    "employee_id": "EMP001",
                    "email": "zhangsan@company.com",
                    "phone_number": "13800138001",
                    "position": "技术总监",
                    "department_id": departments[0].id,
                    "hire_date": date(2020, 1, 15),
                    "status": EmployeeStatus.ACTIVE
                },
                {
                    "name": "李四",
                    "employee_id": "EMP002", 
                    "email": "lisi@company.com",
                    "phone_number": "13800138002",
                    "position": "市场总监",
                    "department_id": departments[1].id,
                    "hire_date": date(2020, 3, 1),
                    "status": EmployeeStatus.ACTIVE
                },
                {
                    "name": "王五",
                    "employee_id": "EMP003",
                    "email": "wangwu@company.com",
                    "phone_number": "13800138003",
                    "position": "人事总监",
                    "department_id": departments[2].id,
                    "hire_date": date(2020, 5, 10),
                    "status": EmployeeStatus.ACTIVE
                },
                {
                    "name": "赵六",
                    "employee_id": "EMP004",
                    "email": "zhaoliu@company.com",
                    "phone_number": "13800138004",
                    "position": "前端开发工程师",
                    "department_id": departments[3].id,
                    "manager_id": None,  # 稍后设置
                    "hire_date": date(2021, 2, 20),
                    "status": EmployeeStatus.ACTIVE
                },
                {
                    "name": "孙七",
                    "employee_id": "EMP005",
                    "email": "sunqi@company.com",
                    "phone_number": "13800138005",
                    "position": "后端开发工程师",
                    "department_id": departments[4].id,
                    "manager_id": None,  # 稍后设置
                    "hire_date": date(2021, 6, 15),
                    "status": EmployeeStatus.ACTIVE
                }
            ]
            
            employees = []
            for emp_data in employees_data:
                employee = EmployeeModel(
                    name=emp_data["name"],
                    employee_id=emp_data["employee_id"],
                    email=emp_data["email"],
                    phone_number=emp_data["phone_number"],
                    position=emp_data["position"],
                    department_id=emp_data["department_id"],
                    hire_date=emp_data["hire_date"],
                    status=emp_data["status"],
                    tenant_id=tenant_id,
                    created_by=created_by
                )
                db.add(employee)
                employees.append(employee)
            
            await db.flush()  # 获取ID
            
            # 设置管理关系
            employees[3].manager_id = employees[0].id  # 赵六的上级是张三
            employees[4].manager_id = employees[0].id  # 孙七的上级是张三
            
            print(f'✅ 创建了{len(employees)}个员工')
            
            # 提交所有更改
            await db.commit()
            print('✅ 所有测试数据创建完成')
            
            # 验证数据
            print('\n📊 数据验证:')
            print(f'   站点: {len(sites)} 个')
            print(f'   部门: {len(departments)} 个')
            print(f'   员工: {len(employees)} 个')
            
            print('\n🎯 测试数据详情:')
            print('站点列表:')
            for site in sites:
                print(f'   • {site.name} (ID: {site.id})')
                
            print('部门列表:')
            for dept in departments:
                print(f'   • {dept.name} (ID: {dept.id}, 站点: {dept.site_id})')
                
            print('员工列表:')
            for emp in employees:
                print(f'   • {emp.name} ({emp.employee_id}) - {emp.position}')
            
            break
            
        except Exception as e:
            await db.rollback()
            print(f'❌ 创建测试数据失败: {str(e)}')
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(create_test_data())
    if success:
        print('\n🎉 基础测试数据创建完成，可以开始API测试！')
    else:
        print('\n💥 测试数据创建失败') 