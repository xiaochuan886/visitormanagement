"""
数据初始化脚本
通过API接口创建测试数据
"""
import sys
import os
import json
import time
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_client import APIClient
from data_init.test_data_generator import TestDataGenerator
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table


class DataInitializer:
    """数据初始化器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化数据初始化器
        
        Args:
            base_url: API基础URL
        """
        self.api_client = APIClient(base_url)
        self.data_generator = TestDataGenerator()
        self.console = Console()
        
        # 存储创建的数据ID，用于清理
        self.created_data = {
            "sites": [],
            "departments": [],
            "employees": [],
            "visitors": []
        }
    
    def login_as_admin(self) -> bool:
        """
        以管理员身份登录
        
        Returns:
            登录是否成功
        """
        try:
            self.console.print("🔐 正在以管理员身份登录...", style="blue")
            login_result = self.api_client.login("admin", "admin123")
            self.console.print("✅ 管理员登录成功", style="green")
            return True
        except Exception as e:
            self.console.print(f"❌ 管理员登录失败: {str(e)}", style="red")
            return False
    
    def create_sites(self, sites_data: List[Dict[str, Any]]) -> List[int]:
        """
        创建站点数据
        
        Args:
            sites_data: 站点数据列表
            
        Returns:
            创建的站点ID列表
        """
        site_ids = []
        
        self.console.print("🏢 正在创建站点数据...", style="blue")
        
        for i, site_data in enumerate(sites_data):
            try:
                response = self.api_client.post("/api/v1/sites", data=site_data)
                
                if response.status_code == 201:
                    site_info = response.json()
                    site_id = site_info.get("id")
                    site_ids.append(site_id)
                    self.created_data["sites"].append(site_id)
                    self.console.print(f"  ✅ 站点 '{site_data['name']}' 创建成功 (ID: {site_id})", style="green")
                else:
                    self.console.print(f"  ❌ 站点 '{site_data['name']}' 创建失败: {response.text}", style="red")
                    
            except Exception as e:
                self.console.print(f"  ❌ 站点 '{site_data['name']}' 创建异常: {str(e)}", style="red")
        
        return site_ids
    
    def create_departments(self, departments_data: List[Dict[str, Any]]) -> List[int]:
        """
        创建部门数据
        
        Args:
            departments_data: 部门数据列表
            
        Returns:
            创建的部门ID列表
        """
        department_ids = []
        
        self.console.print("🏛️ 正在创建部门数据...", style="blue")
        
        for i, dept_data in enumerate(departments_data):
            try:
                response = self.api_client.post("/api/v1/departments", data=dept_data)
                
                if response.status_code == 201:
                    dept_info = response.json()
                    dept_id = dept_info.get("id")
                    department_ids.append(dept_id)
                    self.created_data["departments"].append(dept_id)
                    self.console.print(f"  ✅ 部门 '{dept_data['name']}' 创建成功 (ID: {dept_id})", style="green")
                else:
                    self.console.print(f"  ❌ 部门 '{dept_data['name']}' 创建失败: {response.text}", style="red")
                    
            except Exception as e:
                self.console.print(f"  ❌ 部门 '{dept_data['name']}' 创建异常: {str(e)}", style="red")
        
        return department_ids
    
    def create_employees(self, employees_data: List[Dict[str, Any]]) -> List[int]:
        """
        创建员工数据
        
        Args:
            employees_data: 员工数据列表
            
        Returns:
            创建的员工ID列表
        """
        employee_ids = []
        
        self.console.print("👥 正在创建员工数据...", style="blue")
        
        for i, emp_data in enumerate(employees_data):
            try:
                response = self.api_client.post("/api/v1/employees", data=emp_data)
                
                if response.status_code == 201:
                    emp_info = response.json()
                    emp_id = emp_info.get("id")
                    employee_ids.append(emp_id)
                    self.created_data["employees"].append(emp_id)
                    self.console.print(f"  ✅ 员工 '{emp_data['name']}' 创建成功 (ID: {emp_id})", style="green")
                else:
                    self.console.print(f"  ❌ 员工 '{emp_data['name']}' 创建失败: {response.text}", style="red")
                    
            except Exception as e:
                self.console.print(f"  ❌ 员工 '{emp_data['name']}' 创建异常: {str(e)}", style="red")
        
        return employee_ids
    
    def create_visitors(self, visitors_data: List[Dict[str, Any]]) -> List[int]:
        """
        创建访客数据
        
        Args:
            visitors_data: 访客数据列表
            
        Returns:
            创建的访客ID列表
        """
        visitor_ids = []
        
        self.console.print("🚶 正在创建访客数据...", style="blue")
        
        for i, visitor_data in enumerate(visitors_data):
            try:
                response = self.api_client.post("/api/v1/visitors", data=visitor_data)
                
                if response.status_code == 201:
                    visitor_info = response.json()
                    visitor_id = visitor_info.get("id")
                    visitor_ids.append(visitor_id)
                    self.created_data["visitors"].append(visitor_id)
                    self.console.print(f"  ✅ 访客 '{visitor_data['name']}' 创建成功 (ID: {visitor_id})", style="green")
                else:
                    self.console.print(f"  ❌ 访客 '{visitor_data['name']}' 创建失败: {response.text}", style="red")
                    
            except Exception as e:
                self.console.print(f"  ❌ 访客 '{visitor_data['name']}' 创建异常: {str(e)}", style="red")
        
        return visitor_ids
    
    def initialize_all_data(self) -> Dict[str, List[int]]:
        """
        初始化所有测试数据
        
        Returns:
            创建的数据ID字典
        """
        self.console.print("🚀 开始初始化测试数据...", style="bold blue")
        
        # 登录
        if not self.login_as_admin():
            return {}
        
        # 生成测试数据
        self.console.print("📊 正在生成测试数据...", style="blue")
        test_dataset = self.data_generator.generate_complete_test_dataset()
        
        # 创建数据
        created_ids = {}
        
        # 1. 创建站点
        site_ids = self.create_sites(test_dataset["sites"])
        created_ids["sites"] = site_ids
        
        # 2. 创建部门
        department_ids = self.create_departments(test_dataset["departments"])
        created_ids["departments"] = department_ids
        
        # 3. 创建员工（需要部门ID）
        if department_ids:
            # 更新员工数据中的部门ID
            for emp_data in test_dataset["employees"]:
                emp_data["department_id"] = department_ids[emp_data["department_id"] - 1] if emp_data["department_id"] <= len(department_ids) else department_ids[0]
            
            employee_ids = self.create_employees(test_dataset["employees"])
            created_ids["employees"] = employee_ids
        else:
            self.console.print("⚠️ 没有可用的部门ID，跳过员工创建", style="yellow")
            employee_ids = []
            created_ids["employees"] = []
        
        # 4. 创建访客（需要员工ID和站点ID）
        if employee_ids and site_ids:
            # 更新访客数据中的员工ID和站点ID
            for visitor_data in test_dataset["visitors"]:
                visitor_data["employee_id"] = employee_ids[visitor_data["employee_id"] - 1] if visitor_data["employee_id"] <= len(employee_ids) else employee_ids[0]
                visitor_data["site_id"] = site_ids[visitor_data["site_id"] - 1] if visitor_data["site_id"] <= len(site_ids) else site_ids[0]
            
            visitor_ids = self.create_visitors(test_dataset["visitors"])
            created_ids["visitors"] = visitor_ids
        else:
            self.console.print("⚠️ 没有可用的员工ID或站点ID，跳过访客创建", style="yellow")
            created_ids["visitors"] = []
        
        # 显示统计信息
        self.show_initialization_summary(created_ids)
        
        return created_ids
    
    def show_initialization_summary(self, created_ids: Dict[str, List[int]]):
        """
        显示初始化摘要
        
        Args:
            created_ids: 创建的数据ID字典
        """
        table = Table(title="数据初始化摘要")
        table.add_column("数据类型", style="cyan")
        table.add_column("创建数量", style="green")
        table.add_column("ID范围", style="yellow")
        
        for data_type, ids in created_ids.items():
            if ids:
                id_range = f"{min(ids)} - {max(ids)}" if len(ids) > 1 else str(ids[0])
                table.add_row(
                    data_type.capitalize(),
                    str(len(ids)),
                    id_range
                )
            else:
                table.add_row(
                    data_type.capitalize(),
                    "0",
                    "无"
                )
        
        self.console.print(table)
        
        # 显示API调用统计
        stats = self.api_client.get_stats()
        if stats:
            self.console.print(f"\n📈 API调用统计:", style="bold")
            self.console.print(f"  总请求数: {stats['total_requests']}")
            self.console.print(f"  成功请求: {stats['successful_requests']}")
            self.console.print(f"  失败请求: {stats['failed_requests']}")
            self.console.print(f"  成功率: {stats['success_rate']:.1f}%")
            self.console.print(f"  平均响应时间: {stats['avg_duration_ms']:.2f}ms")
    
    def cleanup_data(self):
        """清理创建的测试数据"""
        self.console.print("🧹 正在清理测试数据...", style="blue")
        
        # 按相反顺序删除（访客 -> 员工 -> 部门 -> 站点）
        cleanup_order = ["visitors", "employees", "departments", "sites"]
        
        for data_type in cleanup_order:
            ids = self.created_data.get(data_type, [])
            if not ids:
                continue
                
            self.console.print(f"  正在删除 {data_type}...", style="blue")
            
            for data_id in ids:
                try:
                    endpoint = f"/api/v1/{data_type}/{data_id}"
                    response = self.api_client.delete(endpoint)
                    
                    if response.status_code in [200, 204]:
                        self.console.print(f"    ✅ 删除 {data_type} ID {data_id} 成功", style="green")
                    else:
                        self.console.print(f"    ❌ 删除 {data_type} ID {data_id} 失败: {response.text}", style="red")
                        
                except Exception as e:
                    self.console.print(f"    ❌ 删除 {data_type} ID {data_id} 异常: {str(e)}", style="red")
        
        # 清空记录
        self.created_data = {
            "sites": [],
            "departments": [],
            "employees": [],
            "visitors": []
        }
        
        self.console.print("✅ 数据清理完成", style="green")
    
    def save_created_data_info(self, created_ids: Dict[str, List[int]], filename: str = "created_data.json"):
        """
        保存创建的数据信息到文件
        
        Args:
            created_ids: 创建的数据ID字典
            filename: 保存的文件名
        """
        data_info = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "created_ids": created_ids,
            "api_stats": self.api_client.get_stats()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_info, f, ensure_ascii=False, indent=2)
        
        self.console.print(f"💾 数据信息已保存到 {filename}", style="green")


def main():
    """主函数"""
    console = Console()
    
    try:
        # 创建数据初始化器
        initializer = DataInitializer()
        
        # 初始化数据
        created_ids = initializer.initialize_all_data()
        
        if created_ids:
            # 保存数据信息
            initializer.save_created_data_info(created_ids)
            
            console.print("\n🎉 数据初始化完成！", style="bold green")
            console.print("现在可以开始API测试了。", style="green")
            
            # 询问是否需要清理数据
            cleanup = input("\n是否需要清理刚创建的测试数据？(y/N): ").lower().strip()
            if cleanup in ['y', 'yes']:
                initializer.cleanup_data()
        else:
            console.print("❌ 数据初始化失败", style="red")
            
    except KeyboardInterrupt:
        console.print("\n⚠️ 用户中断操作", style="yellow")
    except Exception as e:
        console.print(f"\n❌ 初始化过程中发生错误: {str(e)}", style="red")


if __name__ == "__main__":
    main() 