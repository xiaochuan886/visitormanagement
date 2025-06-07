"""
API测试执行脚本
测试访客管理系统的现有API功能
"""
import sys
import os
import json
import time
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.api_client import APIClient
from data_init.test_data_generator import TestDataGenerator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID


class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API测试器
        
        Args:
            base_url: API基础URL
        """
        self.api_client = APIClient(base_url)
        self.data_generator = TestDataGenerator()
        self.console = Console()
        self.test_results = []
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> Dict[str, Any]:
        """
        运行单个测试
        
        Args:
            test_name: 测试名称
            test_func: 测试函数
            *args: 测试函数参数
            **kwargs: 测试函数关键字参数
            
        Returns:
            测试结果
        """
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            test_result = {
                "name": test_name,
                "status": "PASS",
                "duration": duration,
                "result": result,
                "error": None
            }
            
            self.console.print(f"✅ {test_name} - 通过 ({duration:.2f}s)", style="green")
            
        except Exception as e:
            duration = time.time() - start_time
            
            test_result = {
                "name": test_name,
                "status": "FAIL",
                "duration": duration,
                "result": None,
                "error": str(e)
            }
            
            self.console.print(f"❌ {test_name} - 失败: {str(e)} ({duration:.2f}s)", style="red")
        
        self.test_results.append(test_result)
        return test_result
    
    def test_health_check(self) -> Dict[str, Any]:
        """测试健康检查端点"""
        response = self.api_client.get("/health")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"健康检查失败: {response.status_code}")
    
    def test_root_endpoint(self) -> Dict[str, Any]:
        """测试根端点"""
        response = self.api_client.get("/")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"根端点访问失败: {response.status_code}")
    
    def test_login(self) -> Dict[str, Any]:
        """测试用户登录"""
        login_result = self.api_client.login("admin", "admin123")
        
        if not login_result.get("access_token"):
            raise Exception("登录失败：未获取到访问令牌")
        
        return login_result
    
    def test_get_current_user(self) -> Dict[str, Any]:
        """测试获取当前用户信息"""
        user_info = self.api_client.get_current_user()
        
        if not user_info.get("user_id"):
            raise Exception("获取用户信息失败")
        
        return user_info
    
    def test_refresh_token(self) -> Dict[str, Any]:
        """测试刷新令牌"""
        refresh_result = self.api_client.refresh_access_token()
        
        if not refresh_result.get("access_token"):
            raise Exception("刷新令牌失败")
        
        return refresh_result
    
    def test_get_sites(self) -> Dict[str, Any]:
        """测试获取站点列表"""
        response = self.api_client.get("/api/v1/sites")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取站点列表失败: {response.status_code} - {response.text}")
    
    def test_get_site_detail(self) -> Dict[str, Any]:
        """测试获取站点详情"""
        response = self.api_client.get("/api/v1/sites/1")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取站点详情失败: {response.status_code} - {response.text}")
    
    def test_get_departments(self) -> Dict[str, Any]:
        """测试获取部门列表"""
        response = self.api_client.get("/api/v1/departments")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取部门列表失败: {response.status_code} - {response.text}")
    
    def test_get_department_detail(self) -> Dict[str, Any]:
        """测试获取部门详情"""
        response = self.api_client.get("/api/v1/departments/1")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取部门详情失败: {response.status_code} - {response.text}")
    
    def test_get_employees(self) -> Dict[str, Any]:
        """测试获取员工列表"""
        response = self.api_client.get("/api/v1/employees")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取员工列表失败: {response.status_code} - {response.text}")
    
    def test_get_visitors(self) -> Dict[str, Any]:
        """测试获取访客列表"""
        response = self.api_client.get("/api/v1/visitors")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取访客列表失败: {response.status_code} - {response.text}")
    
    def test_create_visitor(self) -> Dict[str, Any]:
        """测试创建访客"""
        visitor_data = self.data_generator.generate_visitor_for_status("pending", 1, 1)
        
        response = self.api_client.post("/api/v1/visitors", data=visitor_data)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"创建访客失败: {response.status_code} - {response.text}")
    
    def test_visitor_lifecycle(self) -> Dict[str, Any]:
        """测试访客完整生命周期"""
        # 1. 创建访客
        visitor_data = self.data_generator.generate_visitor_for_status("pending", 1, 1)
        create_response = self.api_client.post("/api/v1/visitors", data=visitor_data)
        
        if create_response.status_code != 201:
            raise Exception(f"创建访客失败: {create_response.status_code}")
        
        visitor = create_response.json()
        visitor_id = visitor.get("id")
        
        if not visitor_id:
            raise Exception("创建访客成功但未返回ID")
        
        # 2. 获取访客详情
        detail_response = self.api_client.get(f"/api/v1/visitors/{visitor_id}")
        
        if detail_response.status_code != 200:
            raise Exception(f"获取访客详情失败: {detail_response.status_code}")
        
        # 3. 审批访客
        approval_data = {
            "approval_outcome": "approved",
            "approval_comment": "测试审批通过"
        }
        
        approval_response = self.api_client.post(f"/api/v1/visitors/{visitor_id}/approve", data=approval_data)
        
        if approval_response.status_code != 200:
            raise Exception(f"审批访客失败: {approval_response.status_code}")
        
        # 4. 访客签到
        checkin_data = {"checkin_point_id": 1}
        checkin_response = self.api_client.post(f"/api/v1/visitors/{visitor_id}/checkin", data=checkin_data)
        
        if checkin_response.status_code != 200:
            raise Exception(f"访客签到失败: {checkin_response.status_code}")
        
        # 5. 访客签出
        checkout_data = {"checkout_point_id": 1}
        checkout_response = self.api_client.post(f"/api/v1/visitors/{visitor_id}/checkout", data=checkout_data)
        
        if checkout_response.status_code != 200:
            raise Exception(f"访客签出失败: {checkout_response.status_code}")
        
        return {
            "visitor_id": visitor_id,
            "created": visitor,
            "approved": approval_response.json(),
            "checked_in": checkin_response.json(),
            "checked_out": checkout_response.json()
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        self.console.print(Panel.fit("🚀 开始API功能测试", style="bold blue"))
        
        # 基础连接测试
        self.console.print("\n📡 基础连接测试", style="bold cyan")
        self.run_test("健康检查", self.test_health_check)
        self.run_test("根端点访问", self.test_root_endpoint)
        
        # 认证测试
        self.console.print("\n🔐 认证功能测试", style="bold cyan")
        self.run_test("用户登录", self.test_login)
        self.run_test("获取当前用户信息", self.test_get_current_user)
        self.run_test("刷新访问令牌", self.test_refresh_token)
        
        # 站点管理测试
        self.console.print("\n🏢 站点管理测试", style="bold cyan")
        self.run_test("获取站点列表", self.test_get_sites)
        self.run_test("获取站点详情", self.test_get_site_detail)
        
        # 部门管理测试
        self.console.print("\n🏛️ 部门管理测试", style="bold cyan")
        self.run_test("获取部门列表", self.test_get_departments)
        self.run_test("获取部门详情", self.test_get_department_detail)
        
        # 员工管理测试
        self.console.print("\n👥 员工管理测试", style="bold cyan")
        self.run_test("获取员工列表", self.test_get_employees)
        
        # 访客管理测试
        self.console.print("\n🚶 访客管理测试", style="bold cyan")
        self.run_test("获取访客列表", self.test_get_visitors)
        self.run_test("创建访客", self.test_create_visitor)
        
        # 业务流程测试
        self.console.print("\n🔄 业务流程测试", style="bold cyan")
        self.run_test("访客完整生命周期", self.test_visitor_lifecycle)
        
        # 显示测试结果摘要
        self.show_test_summary()
    
    def show_test_summary(self):
        """显示测试结果摘要"""
        self.console.print("\n" + "="*60, style="bold")
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        
        # 创建结果表格
        table = Table(title="测试结果摘要")
        table.add_column("测试名称", style="cyan")
        table.add_column("状态", style="bold")
        table.add_column("耗时(秒)", style="yellow")
        table.add_column("错误信息", style="red")
        
        for result in self.test_results:
            status_style = "green" if result["status"] == "PASS" else "red"
            status_text = "✅ 通过" if result["status"] == "PASS" else "❌ 失败"
            
            table.add_row(
                result["name"],
                f"[{status_style}]{status_text}[/{status_style}]",
                f"{result['duration']:.2f}",
                result["error"] or ""
            )
        
        self.console.print(table)
        
        # 显示统计信息
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        stats_panel = Panel(
            f"总测试数: {total_tests}\n"
            f"通过: {passed_tests}\n"
            f"失败: {failed_tests}\n"
            f"成功率: {success_rate:.1f}%",
            title="测试统计",
            style="bold"
        )
        
        self.console.print(stats_panel)
        
        # 显示API调用统计
        api_stats = self.api_client.get_stats()
        if api_stats:
            api_panel = Panel(
                f"总请求数: {api_stats['total_requests']}\n"
                f"成功请求: {api_stats['successful_requests']}\n"
                f"失败请求: {api_stats['failed_requests']}\n"
                f"成功率: {api_stats['success_rate']:.1f}%\n"
                f"平均响应时间: {api_stats['avg_duration_ms']:.2f}ms",
                title="API调用统计",
                style="bold"
            )
            
            self.console.print(api_panel)
    
    def save_test_report(self, filename: str = "test_report.json"):
        """
        保存测试报告
        
        Args:
            filename: 报告文件名
        """
        report = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for result in self.test_results if result["status"] == "PASS"),
            "failed_tests": sum(1 for result in self.test_results if result["status"] == "FAIL"),
            "test_results": self.test_results,
            "api_stats": self.api_client.get_stats(),
            "request_logs": self.api_client.get_request_logs()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.console.print(f"💾 测试报告已保存到 {filename}", style="green")


def main():
    """主函数"""
    console = Console()
    
    try:
        # 创建API测试器
        tester = APITester()
        
        # 运行所有测试
        tester.run_all_tests()
        
        # 保存测试报告
        tester.save_test_report()
        
        console.print("\n🎉 API测试完成！", style="bold green")
        
    except KeyboardInterrupt:
        console.print("\n⚠️ 用户中断测试", style="yellow")
    except Exception as e:
        console.print(f"\n❌ 测试过程中发生错误: {str(e)}", style="red")


if __name__ == "__main__":
    main() 