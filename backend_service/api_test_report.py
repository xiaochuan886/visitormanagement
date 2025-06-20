"""
访客管理系统 - API测试报告生成器
用于后端测试完善和前端开发交接
"""
import asyncio
import aiohttp
import json
from datetime import datetime, date, time
from typing import Dict, List, Any


class APITestReporter:
    """API测试报告生成器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
        self.test_results = []
        
    async def login(self) -> bool:
        """登录并获取认证token"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": "admin", "password": "admin123"},
                    timeout=10
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        self.auth_token = result.get("access_token")
                        return True
                    return False
            except Exception:
                return False
    
    async def test_endpoint(self, method: str, path: str, name: str, 
                          data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """测试单个API端点"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            headers["Content-Type"] = "application/json"
        
        test_result = {
            "name": name,
            "method": method,
            "path": path,
            "status": "unknown",
            "http_status": 0,
            "response_data": None,
            "error_message": None,
            "records_count": 0
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(f"{self.base_url}{path}", headers=headers, timeout=10) as resp:
                        test_result["http_status"] = resp.status
                        if resp.status == expected_status:
                            result = await resp.json()
                            test_result["response_data"] = result
                            test_result["status"] = "success"
                            
                            # 计算记录数
                            if isinstance(result, dict):
                                if "items" in result:
                                    test_result["records_count"] = len(result["items"])
                                    test_result["total_records"] = result.get("total", 0)
                                elif "id" in result:
                                    test_result["records_count"] = 1
                            elif isinstance(result, list):
                                test_result["records_count"] = len(result)
                        else:
                            test_result["status"] = "failed"
                            test_result["error_message"] = await resp.text()
                
                elif method == "POST":
                    async with session.post(
                        f"{self.base_url}{path}",
                        json=data,
                        headers=headers,
                        timeout=10
                    ) as resp:
                        test_result["http_status"] = resp.status
                        if resp.status in [200, 201]:
                            result = await resp.json()
                            test_result["response_data"] = result
                            test_result["status"] = "success"
                            test_result["records_count"] = 1
                        else:
                            test_result["status"] = "failed"
                            test_result["error_message"] = await resp.text()
                            
            except asyncio.TimeoutError:
                test_result["status"] = "timeout"
                test_result["error_message"] = "请求超时"
            except Exception as e:
                test_result["status"] = "error"
                test_result["error_message"] = str(e)
        
        return test_result
    
    async def run_comprehensive_test(self) -> List[Dict[str, Any]]:
        """运行完整的API测试"""
        print("🚀 开始API综合测试")
        print("=" * 60)
        
        # 1. 认证测试
        if not await self.login():
            print("❌ 认证失败，无法继续测试")
            return []
        
        print("✅ 认证成功")
        
        # 2. 定义测试用例
        test_cases = [
            # 基础端点
            ("GET", "/health", "系统健康检查", None, 200),
            ("GET", "/docs", "API文档", None, 200),
            
            # 核心业务端点
            ("GET", "/api/v1/employees/", "员工列表", None, 200),
            ("GET", "/api/v1/departments/", "部门列表", None, 200),
            ("GET", "/api/v1/sites/", "站点列表", None, 200),
            ("GET", "/api/v1/visitors/", "访客列表", None, 200),
            
            # 详情端点测试
            ("GET", "/api/v1/employees/1", "员工详情", None, 200),
            ("GET", "/api/v1/departments/6", "部门详情", None, 200),
            ("GET", "/api/v1/sites/5", "站点详情", None, 200),
            
            # 创建操作测试 - 修复日期格式
            ("POST", "/api/v1/visitors/", "创建访客", {
                "name": "API测试访客",
                "email": "apitest@company.com",
                "phone_number": "13800138000",
                "company_name": "API测试公司",
                "purpose": "business",
                "expected_date": "2025-06-21T14:00:00",  # 使用正确的datetime格式
                "expected_time": "14:00:00",
                "privacy_policy": True,
                "promise": True
            }, 201),
        ]
        
        # 3. 执行测试
        for method, path, name, data, expected_status in test_cases:
            print(f"🔍 测试: {name}")
            result = await self.test_endpoint(method, path, name, data, expected_status)
            self.test_results.append(result)
            
            # 输出结果
            if result["status"] == "success":
                if result.get("records_count", 0) > 0:
                    print(f"   ✅ 成功 - HTTP {result['http_status']} ({result['records_count']} 条记录)")
                else:
                    print(f"   ✅ 成功 - HTTP {result['http_status']}")
            else:
                print(f"   ❌ 失败 - HTTP {result['http_status']} - {result['error_message'][:50]}...")
        
        return self.test_results
    
    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "无测试结果"
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["status"] == "success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests) * 100
        
        report = f"""
📊 访客管理系统API测试报告
{"=" * 50}

🎯 测试概览:
   • 总测试数: {total_tests}
   • 成功数: {successful_tests}
   • 失败数: {failed_tests}
   • 成功率: {success_rate:.1f}%

📋 详细结果:
"""
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            report += f"""
{status_icon} {result['name']}
   方法: {result['method']} {result['path']}
   状态: HTTP {result['http_status']} - {result['status']}
"""
            if result["status"] == "success" and result.get("records_count", 0) > 0:
                report += f"   数据: {result['records_count']} 条记录\n"
            elif result["status"] != "success" and result["error_message"]:
                report += f"   错误: {result['error_message'][:100]}...\n"
        
        # 问题总结
        failed_results = [r for r in self.test_results if r["status"] != "success"]
        if failed_results:
            report += f"""
⚠️  需要修复的问题:
"""
            for result in failed_results:
                report += f"   • {result['name']}: {result['error_message'][:100]}...\n"
        
        # 成功的API
        successful_results = [r for r in self.test_results if r["status"] == "success"]
        if successful_results:
            report += f"""
🎉 可用于前端开发的API端点:
"""
            for result in successful_results:
                report += f"   • {result['method']} {result['path']} - {result['name']}\n"
        
        # 前端开发指南
        report += f"""
📖 前端开发指南:
   • 认证方式: Bearer Token
   • 基础URL: {self.base_url}
   • 认证端点: POST /api/v1/auth/login
   • 数据格式: JSON
   • 响应格式: 统一响应结构

🔧 后续工作建议:
   1. 修复失败的API端点
   2. 完善API文档和示例
   3. 增加错误处理和验证
   4. 提供Postman集合或OpenAPI规范
   5. 创建前端集成指南
"""
        
        return report
    
    def save_report(self, filename: str = "api_test_report.md") -> None:
        """保存测试报告到文件"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 测试报告已保存到: {filename}")


async def main():
    """主函数"""
    tester = APITestReporter()
    
    # 运行测试
    await tester.run_comprehensive_test()
    
    # 生成并输出报告
    report = tester.generate_report()
    print(report)
    
    # 保存报告
    tester.save_report()
    
    # 总结建议
    success_rate = len([r for r in tester.test_results if r["status"] == "success"]) / len(tester.test_results) * 100
    if success_rate >= 80:
        print(f"🎉 后端API测试通过率{success_rate:.1f}%，可以开始前端开发！")
    else:
        print(f"⚠️  后端API测试通过率{success_rate:.1f}%，建议先修复失败的端点")
        failed_results = [r for r in tester.test_results if r["status"] != "success"]
        print("📋 优先修复工作:")
        for result in failed_results:
            print(f"   • {result['name']}: {result['error_message'][:100]}...")


if __name__ == "__main__":
    asyncio.run(main()) 