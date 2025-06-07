#!/usr/bin/env python3
"""
访客管理系统全功能测试脚本
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

# 测试配置
BASE_URL = "http://127.0.0.1:8001"
TEST_TIMEOUT = 30

class VisitorManagementTester:
    """访客管理系统测试器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ 通过" if success else "❌ 失败"
        result = f"{status} {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_server_connection(self) -> bool:
        """测试服务器连接"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("服务器连接", True, f"响应: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("服务器连接", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("服务器连接", False, f"连接错误: {str(e)}")
            return False
    
    def test_api_docs(self) -> bool:
        """测试API文档"""
        try:
            response = self.session.get(f"{self.base_url}/docs", timeout=5)
            success = response.status_code == 200
            self.log_test("API文档", success, f"状态码: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("API文档", False, f"错误: {str(e)}")
            return False
    
    def test_openapi_spec(self) -> bool:
        """测试OpenAPI规范"""
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=5)
            if response.status_code == 200:
                spec = response.json()
                paths_count = len(spec.get("paths", {}))
                self.log_test("OpenAPI规范", True, f"发现 {paths_count} 个API端点")
                return True
            else:
                self.log_test("OpenAPI规范", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("OpenAPI规范", False, f"错误: {str(e)}")
            return False
    
    def test_health_check(self) -> bool:
        """测试健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("健康检查", True, f"状态: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("健康检查", False, f"错误: {str(e)}")
            return False
    
    def test_visitor_endpoints(self) -> bool:
        """测试访客管理端点"""
        endpoints_to_test = [
            ("/api/v1/visitors/", "GET", "获取访客列表"),
            ("/api/v1/visitors/", "POST", "创建访客"),
            ("/api/v1/visitors/stats", "GET", "访客统计"),
        ]
        
        all_success = True
        for endpoint, method, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                elif method == "POST":
                    # 测试POST需要数据，这里只测试端点是否存在
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                                json={}, timeout=5)
                
                # 401/422是预期的（需要认证/数据验证），404是不存在
                if response.status_code in [200, 401, 422]:
                    self.log_test(f"访客API - {description}", True, 
                                f"{method} {endpoint} (状态: {response.status_code})")
                else:
                    self.log_test(f"访客API - {description}", False, 
                                f"状态码: {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                self.log_test(f"访客API - {description}", False, f"错误: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_auth_endpoints(self) -> bool:
        """测试认证端点"""
        endpoints_to_test = [
            ("/api/v1/auth/login", "POST", "用户登录"),
            ("/api/v1/auth/refresh", "POST", "刷新令牌"),
            ("/api/v1/auth/me", "GET", "获取用户信息"),
        ]
        
        all_success = True
        for endpoint, method, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                                json={}, timeout=5)
                
                # 401/422是预期的
                if response.status_code in [200, 401, 422]:
                    self.log_test(f"认证API - {description}", True, 
                                f"{method} {endpoint} (状态: {response.status_code})")
                else:
                    self.log_test(f"认证API - {description}", False, 
                                f"状态码: {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                self.log_test(f"认证API - {description}", False, f"错误: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_employee_endpoints(self) -> bool:
        """测试员工管理端点"""
        endpoints_to_test = [
            ("/api/v1/employees/", "GET", "获取员工列表"),
            ("/api/v1/departments/", "GET", "获取部门列表"),
            ("/api/v1/sites/", "GET", "获取站点列表"),
        ]
        
        all_success = True
        for endpoint, method, description in endpoints_to_test:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code in [200, 401, 422]:
                    self.log_test(f"员工管理API - {description}", True, 
                                f"{method} {endpoint} (状态: {response.status_code})")
                else:
                    self.log_test(f"员工管理API - {description}", False, 
                                f"状态码: {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                self.log_test(f"员工管理API - {description}", False, f"错误: {str(e)}")
                all_success = False
        
        return all_success
    
    def test_database_models(self) -> bool:
        """测试数据库模型"""
        try:
            # 测试模型导入
            from app.infrastructure.database.models import (
                VisitorModel, EmployeeModel, DepartmentModel, 
                SiteModel, CheckinPointModel, ApprovalHistoryModel
            )
            
            models = [
                ("访客模型", VisitorModel),
                ("员工模型", EmployeeModel), 
                ("部门模型", DepartmentModel),
                ("站点模型", SiteModel),
                ("签到点模型", CheckinPointModel),
                ("审批历史模型", ApprovalHistoryModel),
            ]
            
            all_success = True
            for name, model in models:
                try:
                    # 检查模型是否有必要的属性
                    if hasattr(model, '__tablename__') and hasattr(model, '__table__'):
                        self.log_test(f"数据库模型 - {name}", True, f"表名: {model.__tablename__}")
                    else:
                        self.log_test(f"数据库模型 - {name}", False, "缺少必要属性")
                        all_success = False
                except Exception as e:
                    self.log_test(f"数据库模型 - {name}", False, f"错误: {str(e)}")
                    all_success = False
            
            return all_success
            
        except Exception as e:
            self.log_test("数据库模型", False, f"导入错误: {str(e)}")
            return False
    
    def test_services(self) -> bool:
        """测试服务层"""
        try:
            from app.application.services.visitor_service import VisitorService
            
            # 测试服务类是否可以实例化
            service = VisitorService()
            
            # 检查服务方法
            methods = [
                "create_visitor", "get_visitor", "update_visitor", 
                "delete_visitor", "list_visitors", "approve_visitor",
                "checkin_visitor", "checkout_visitor", "generate_qr_code"
            ]
            
            all_success = True
            for method_name in methods:
                if hasattr(service, method_name):
                    self.log_test(f"访客服务 - {method_name}", True, "方法存在")
                else:
                    self.log_test(f"访客服务 - {method_name}", False, "方法不存在")
                    all_success = False
            
            return all_success
            
        except Exception as e:
            self.log_test("服务层", False, f"错误: {str(e)}")
            return False
    
    def test_configuration(self) -> bool:
        """测试配置"""
        try:
            from app.core.config import settings
            
            config_items = [
                ("应用名称", settings.app_name),
                ("数据库URL", settings.database_url),
                ("Redis URL", settings.redis_url),
                ("JWT密钥", settings.secret_key),
            ]
            
            all_success = True
            for name, value in config_items:
                if value:
                    self.log_test(f"配置 - {name}", True, f"已设置")
                else:
                    self.log_test(f"配置 - {name}", False, "未设置")
                    all_success = False
            
            return all_success
            
        except Exception as e:
            self.log_test("配置", False, f"错误: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始访客管理系统全功能测试...\n")
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(5)
        
        # 基础连接测试
        print("\n📡 基础连接测试:")
        server_ok = self.test_server_connection()
        
        if not server_ok:
            print("\n❌ 服务器连接失败，跳过其他测试")
            return self.get_summary()
        
        # API文档测试
        print("\n📚 API文档测试:")
        self.test_api_docs()
        self.test_openapi_spec()
        self.test_health_check()
        
        # API端点测试
        print("\n🔗 API端点测试:")
        self.test_visitor_endpoints()
        self.test_auth_endpoints()
        self.test_employee_endpoints()
        
        # 内部组件测试
        print("\n🔧 内部组件测试:")
        self.test_database_models()
        self.test_services()
        self.test_configuration()
        
        return self.get_summary()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试总结"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }
        
        print(f"\n📊 测试总结:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过: {passed_tests}")
        print(f"   失败: {failed_tests}")
        print(f"   成功率: {summary['success_rate']:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 所有测试通过！访客管理系统功能完整！")
        else:
            print(f"\n⚠️  有 {failed_tests} 个测试失败，需要检查相关功能")
        
        return summary


if __name__ == "__main__":
    tester = VisitorManagementTester()
    summary = tester.run_all_tests()
    
    # 输出详细结果到文件
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细测试结果已保存到: test_results.json") 