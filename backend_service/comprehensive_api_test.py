#!/usr/bin/env python3
"""
访客管理系统 - 综合API测试脚本
测试所有主要API功能
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiohttp
import sys

class APITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] {status} {test_name}"
        if details:
            message += f" - {details}"
        print(message)
        
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.access_token:
            headers['Authorization'] = f"Bearer {self.access_token}"
        
        kwargs['headers'] = headers
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    data = await response.json()
                except:
                    data = {"text": await response.text()}
                
                return {
                    "status_code": response.status,
                    "data": data,
                    "success": 200 <= response.status < 300
                }
        except Exception as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    async def test_health_check(self):
        """测试健康检查"""
        print("\n🔍 测试系统健康状态...")
        
        # 测试根路径
        result = await self.make_request("GET", "/")
        self.log_test(
            "根路径访问", 
            result["success"], 
            f"状态码: {result['status_code']}"
        )
        
        # 测试健康检查
        result = await self.make_request("GET", "/health")
        self.log_test(
            "健康检查", 
            result["success"], 
            f"状态码: {result['status_code']}"
        )
    
    async def test_authentication(self):
        """测试认证功能"""
        print("\n🔐 测试认证功能...")
        
        # 测试登录
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        result = await self.make_request(
            "POST", 
            "/api/v1/auth/login",
            json=login_data
        )
        
        if result["success"] and "access_token" in result["data"]:
            self.access_token = result["data"]["access_token"]
            self.log_test("用户登录", True, "获取到访问令牌")
        else:
            self.log_test("用户登录", False, f"登录失败: {result['data']}")
            return False
        
        # 测试获取用户信息
        result = await self.make_request(
            "GET", 
            f"/api/v1/auth/me?token={self.access_token}"
        )
        
        self.log_test(
            "获取用户信息", 
            result["success"], 
            f"用户: {result['data'].get('username', 'N/A')}" if result["success"] else str(result["data"])
        )
        
        return True
    
    async def test_sites_api(self):
        """测试站点API"""
        print("\n🏢 测试站点管理...")
        
        # 获取站点列表
        result = await self.make_request("GET", "/api/v1/sites/")
        self.log_test(
            "获取站点列表", 
            result["success"], 
            f"找到 {result['data'].get('total', 0)} 个站点" if result["success"] else str(result["data"])
        )
        
        # 创建测试站点
        site_data = {
            "name": "测试站点",
            "code": f"TEST_{int(time.time())}",
            "address": "测试地址123号",
            "city": "北京",
            "province": "北京市",
            "description": "API测试创建的站点"
        }
        
        result = await self.make_request(
            "POST", 
            "/api/v1/sites/",
            json=site_data
        )
        
        site_id = None
        if result["success"] and "id" in result["data"]:
            site_id = result["data"]["id"]
            self.log_test("创建站点", True, f"站点ID: {site_id}")
        else:
            self.log_test("创建站点", False, str(result["data"]))
        
        # 如果创建成功，测试获取和更新
        if site_id:
            # 获取单个站点
            result = await self.make_request("GET", f"/api/v1/sites/{site_id}")
            self.log_test(
                "获取站点详情", 
                result["success"], 
                f"站点名称: {result['data'].get('name', 'N/A')}" if result["success"] else str(result["data"])
            )
            
            # 更新站点
            update_data = {
                "name": "更新后的测试站点",
                "description": "已更新的描述"
            }
            
            result = await self.make_request(
                "PUT", 
                f"/api/v1/sites/{site_id}",
                json=update_data
            )
            self.log_test(
                "更新站点", 
                result["success"], 
                "站点信息已更新" if result["success"] else str(result["data"])
            )
            
            return site_id
        
        return None
    
    async def test_departments_api(self):
        """测试部门API"""
        print("\n🏛️ 测试部门管理...")
        
        # 获取部门列表
        result = await self.make_request("GET", "/api/v1/departments/")
        self.log_test(
            "获取部门列表", 
            result["success"], 
            f"找到 {result['data'].get('total', 0)} 个部门" if result["success"] else str(result["data"])
        )
        
        # 创建测试部门
        dept_data = {
            "name": "测试部门",
            "code": f"DEPT_{int(time.time())}",
            "description": "API测试创建的部门"
        }
        
        result = await self.make_request(
            "POST", 
            "/api/v1/departments/",
            json=dept_data
        )
        
        dept_id = None
        if result["success"] and "id" in result["data"]:
            dept_id = result["data"]["id"]
            self.log_test("创建部门", True, f"部门ID: {dept_id}")
        else:
            self.log_test("创建部门", False, str(result["data"]))
        
        return dept_id
    
    async def test_employees_api(self, dept_id=None):
        """测试员工API"""
        print("\n👥 测试员工管理...")
        
        # 获取员工列表
        result = await self.make_request("GET", "/api/v1/employees/")
        self.log_test(
            "获取员工列表", 
            result["success"], 
            f"找到 {result['data'].get('total', 0)} 个员工" if result["success"] else str(result["data"])
        )
        
        # 如果没有部门ID，跳过创建员工
        if not dept_id:
            self.log_test("创建员工", False, "需要先创建部门")
            return None
        
        # 创建测试员工
        employee_data = {
            "name": "测试员工",
            "employee_id": f"EMP_{int(time.time())}",  # 使用正确的字段名
            "email": f"test_{int(time.time())}@example.com",
            "phone_number": "13800138000",
            "department_id": dept_id,  # 使用创建的部门ID
            "gender": "male",
            "status": "active"
        }
        
        result = await self.make_request(
            "POST", 
            "/api/v1/employees/",
            json=employee_data
        )
        
        employee_id = None
        if result["success"] and "id" in result["data"]:
            employee_id = result["data"]["id"]
            self.log_test("创建员工", True, f"员工ID: {employee_id}")
        else:
            self.log_test("创建员工", False, str(result["data"]))
        
        return employee_id
    
    async def test_visitors_api(self):
        """测试访客API"""
        print("\n🚶 测试访客管理...")
        
        # 获取访客列表
        result = await self.make_request("GET", "/api/v1/visitors/")
        self.log_test(
            "获取访客列表", 
            result["success"], 
            f"找到 {result['data'].get('total', 0)} 个访客" if result["success"] else str(result["data"])
        )
        
        # 创建测试访客
        visitor_data = {
            "name": "测试访客",
            "phone_number": "13900139000",
            "email": f"visitor_{int(time.time())}@example.com",
            "company_name": "测试公司",
            "purpose": "business",
            "expected_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "gender": "male",
            "status": "pending"
        }
        
        result = await self.make_request(
            "POST", 
            "/api/v1/visitors/",
            json=visitor_data
        )
        
        visitor_id = None
        if result["success"] and "id" in result["data"]:
            visitor_id = result["data"]["id"]
            self.log_test("创建访客", True, f"访客ID: {visitor_id}")
        else:
            self.log_test("创建访客", False, str(result["data"]))
        
        return visitor_id
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n⚠️ 测试错误处理...")
        
        # 测试无效的端点
        result = await self.make_request("GET", "/api/v1/nonexistent")
        self.log_test(
            "无效端点处理", 
            result["status_code"] == 404, 
            f"状态码: {result['status_code']}"
        )
        
        # 测试无效的站点ID
        result = await self.make_request("GET", "/api/v1/sites/99999")
        self.log_test(
            "无效资源ID处理", 
            result["status_code"] == 404, 
            f"状态码: {result['status_code']}"
        )
        
        # 测试无效的JSON数据
        result = await self.make_request(
            "POST", 
            "/api/v1/sites/",
            json={"invalid": "data"}
        )
        self.log_test(
            "无效数据验证", 
            result["status_code"] in [400, 422], 
            f"状态码: {result['status_code']}"
        )
    
    async def test_performance(self):
        """测试性能"""
        print("\n⚡ 测试API性能...")
        
        # 并发请求测试
        start_time = time.time()
        tasks = []
        
        for i in range(10):
            task = self.make_request("GET", "/api/v1/sites/")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        successful_requests = sum(1 for r in results if r["success"])
        total_time = end_time - start_time
        
        self.log_test(
            "并发请求测试", 
            successful_requests >= 8, 
            f"{successful_requests}/10 成功, 耗时: {total_time:.2f}秒"
        )
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("📊 测试总结报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        print("\n" + "="*60)
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始访客管理系统综合API测试")
        print(f"测试目标: {self.base_url}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 基础测试
            await self.test_health_check()
            
            # 认证测试
            auth_success = await self.test_authentication()
            if not auth_success:
                print("❌ 认证失败，跳过需要认证的测试")
                return
            
            # 功能测试
            site_id = await self.test_sites_api()
            dept_id = await self.test_departments_api()
            employee_id = await self.test_employees_api(dept_id)
            visitor_id = await self.test_visitors_api()
            
            # 错误处理测试
            await self.test_error_handling()
            
            # 性能测试
            await self.test_performance()
            
            # 清理测试数据
            print("\n🧹 清理测试数据...")
            if site_id:
                result = await self.make_request("DELETE", f"/api/v1/sites/{site_id}")
                self.log_test("清理测试站点", result["success"], f"站点ID: {site_id}")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
        
        finally:
            self.print_summary()


async def main():
    """主函数"""
    # 检查服务器是否运行
    print("🔍 检查服务器状态...")
    
    async with APITester() as tester:
        # 简单的连接测试
        result = await tester.make_request("GET", "/")
        if not result["success"]:
            print("❌ 无法连接到服务器，请确保应用正在运行在 http://127.0.0.1:8000")
            print("💡 启动命令: python3 main.py")
            sys.exit(1)
        
        print("✅ 服务器连接正常")
        
        # 运行所有测试
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1) 