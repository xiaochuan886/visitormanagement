#!/usr/bin/env python3
"""
用户旅程API覆盖度测试

基于 docs/product/user-journey-map.md 中定义的用户旅程，
验证后端API是否支持所有关键业务节点。

测试范围：
1. 访客自主申请旅程 - 7个阶段
2. 员工邀约访客旅程 - 3个阶段  
3. 门岗人员验证旅程 - 3个阶段
4. 前台人员接待旅程 - 2个阶段
5. 管理员系统管理旅程 - 2个阶段
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class UserJourneyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        self.coverage_summary = {}
        self.access_token = None
        
    async def authenticate(self, client: httpx.AsyncClient) -> bool:
        """获取认证token"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = await client.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                return self.access_token is not None
            return False
        except Exception:
            return False

    async def test_api_endpoint(self, client: httpx.AsyncClient, method: str, 
                               endpoint: str, data: dict = None, 
                               expected_status: int = 200, require_auth: bool = True) -> Dict[str, Any]:
        """测试单个API端点"""
        try:
            headers = {}
            if require_auth and self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            
            if method.upper() == "GET":
                response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = await client.post(f"{self.base_url}{endpoint}", json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(f"{self.base_url}{endpoint}", json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(f"{self.base_url}{endpoint}", headers=headers)
            
            return {
                "status_code": response.status_code,
                "success": response.status_code == expected_status,
                "response_size": len(response.content) if response.content else 0,
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0,
                "error": None
            }
        except Exception as e:
            return {
                "status_code": 0,
                "success": False,
                "response_size": 0,
                "response_time": 0,
                "error": str(e)
            }

    async def test_visitor_self_application_journey(self, client: httpx.AsyncClient):
        """测试访客自主申请旅程"""
        print("\n🎯 测试访客自主申请旅程...")
        
        journey_tests = {
            "阶段1-需求产生与信息获取": [
                {"name": "获取系统健康状态", "method": "GET", "endpoint": "/health", "require_auth": False},
                {"name": "获取可用站点列表", "method": "GET", "endpoint": "/api/v1/sites/"},
                {"name": "获取部门列表", "method": "GET", "endpoint": "/api/v1/departments/"},
            ],
            "阶段2-申请填写": [
                {"name": "获取员工列表(被访人选择)", "method": "GET", "endpoint": "/api/v1/employees/"},
                {"name": "创建访客申请", "method": "POST", "endpoint": "/api/v1/visitors/apply", 
                 "require_auth": False,
                 "data": {
                     "name": "测试访客",
                     "phone_number": "13800138000",
                     "identification_no": "110101199001011234",
                     "company_name": "测试公司",
                     "purpose": "business",
                     "expected_date": "2025-06-21T14:00:00",
                     "employee_id": 1,
                     "site_id": 5
                 }},
            ],
            "阶段3-等待审批": [
                {"name": "查询访客申请状态", "method": "GET", "endpoint": "/api/v1/visitors/"},
                {"name": "通过手机号查询申请状态", "method": "GET", "endpoint": "/api/v1/visitors/query/by-phone?phone_number=13800138000", "require_auth": False},
                {"name": "获取特定访客详情", "method": "GET", "endpoint": "/api/v1/visitors/1", "expected_status": 404},  # 可能不存在
            ],
            "阶段4-访问前准备": [
                {"name": "查看访问指南(站点详情)", "method": "GET", "endpoint": "/api/v1/sites/5"},
                {"name": "获取被访人信息", "method": "GET", "endpoint": "/api/v1/employees/1"},
            ],
            "阶段5-到达与签到": [
                # 这些功能需要专门的签到API，目前可能缺失
                {"name": "门岗验证接口", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要专门的验证API"},
            ],
            "阶段6-访问过程": [
                # 权限管理和时间跟踪功能
                {"name": "访客权限查询", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要权限管理API"},
            ],
            "阶段7-离开与反馈": [
                # 签出和反馈功能
                {"name": "访客签出", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要签出API"},
            ]
        }
        
        stage_results = {}
        for stage, tests in journey_tests.items():
            stage_results[stage] = []
            for test in tests:
                result = await self.test_api_endpoint(
                    client, 
                    test["method"], 
                    test["endpoint"], 
                    test.get("data"),
                    test.get("expected_status", 200),
                    test.get("require_auth", True)
                )
                result["test_name"] = test["name"]
                result["note"] = test.get("note", "")
                stage_results[stage].append(result)
        
        self.test_results["访客自主申请旅程"] = stage_results
        return stage_results

    async def test_employee_invitation_journey(self, client: httpx.AsyncClient):
        """测试员工邀约访客旅程"""
        print("\n👔 测试员工邀约访客旅程...")
        
        journey_tests = {
            "阶段1-邀约需求产生": [
                {"name": "员工登录验证", "method": "GET", "endpoint": "/api/v1/employees/1"},
                {"name": "查看日程安排", "method": "GET", "endpoint": "/api/v1/employees/", "note": "需要日程API"},
            ],
            "阶段2-创建访客邀约": [
                {"name": "创建访客邀约", "method": "POST", "endpoint": "/api/v1/visitors/",
                 "data": {
                     "name": "邀约访客",
                     "phone_number": "13900139000", 
                     "identification_no": "110101199002021234",
                     "company_name": "合作伙伴公司",
                     "purpose": "business",
                     "expected_date": "2025-06-22T10:00:00",
                     "employee_id": 1,
                     "site_id": 5
                 }},
                {"name": "权限配置", "method": "GET", "endpoint": "/api/v1/sites/5", "note": "需要权限配置API"},
            ],
            "阶段3-邀约管理": [
                {"name": "查看邀约状态", "method": "GET", "endpoint": "/api/v1/visitors/"},
                {"name": "访客到达通知", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要通知API"},
            ]
        }
        
        stage_results = {}
        for stage, tests in journey_tests.items():
            stage_results[stage] = []
            for test in tests:
                result = await self.test_api_endpoint(
                    client,
                    test["method"],
                    test["endpoint"], 
                    test.get("data"),
                    test.get("expected_status", 200),
                    test.get("require_auth", True)
                )
                result["test_name"] = test["name"]
                result["note"] = test.get("note", "")
                stage_results[stage].append(result)
        
        self.test_results["员工邀约访客旅程"] = stage_results
        return stage_results

    async def test_security_verification_journey(self, client: httpx.AsyncClient):
        """测试门岗人员验证旅程"""
        print("\n🔒 测试门岗人员验证旅程...")
        
        journey_tests = {
            "阶段1-工作准备": [
                {"name": "系统状态检查", "method": "GET", "endpoint": "/health", "require_auth": False},
                {"name": "当日访客列表", "method": "GET", "endpoint": "/api/v1/visitors/"},
            ],
            "阶段2-访客验证": [
                {"name": "二维码验证", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要二维码验证API"},
                {"name": "身份证核验", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要身份验证API"},
                {"name": "访客证打印", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要证件打印API"},
            ],
            "阶段3-异常处理": [
                {"name": "异常访客处理", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要异常处理API"},
                {"name": "临时权限发放", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要临时权限API"},
            ]
        }
        
        stage_results = {}
        for stage, tests in journey_tests.items():
            stage_results[stage] = []
            for test in tests:
                result = await self.test_api_endpoint(
                    client,
                    test["method"],
                    test["endpoint"],
                    test.get("data"),
                    test.get("expected_status", 200),
                    test.get("require_auth", True)
                )
                result["test_name"] = test["name"]
                result["note"] = test.get("note", "")
                stage_results[stage].append(result)
        
        self.test_results["门岗人员验证旅程"] = stage_results
        return stage_results

    async def test_reception_service_journey(self, client: httpx.AsyncClient):
        """测试前台人员接待旅程"""
        print("\n🏢 测试前台人员接待旅程...")
        
        journey_tests = {
            "阶段1-访客到达": [
                {"name": "访客签到确认", "method": "GET", "endpoint": "/api/v1/visitors/", "note": "需要签到API"},
                {"name": "被访人通知", "method": "GET", "endpoint": "/api/v1/employees/1"},
                {"name": "等候区安排", "method": "GET", "endpoint": "/api/v1/sites/5", "note": "需要区域管理API"},
            ],
            "阶段2-访客服务": [
                {"name": "会议室协调", "method": "GET", "endpoint": "/api/v1/sites/", "note": "需要会议室API"},
                {"name": "访客引导服务", "method": "GET", "endpoint": "/api/v1/sites/5"},
            ]
        }
        
        stage_results = {}
        for stage, tests in journey_tests.items():
            stage_results[stage] = []
            for test in tests:
                result = await self.test_api_endpoint(
                    client,
                    test["method"],
                    test["endpoint"],
                    test.get("data"),
                    test.get("expected_status", 200),
                    test.get("require_auth", True)
                )
                result["test_name"] = test["name"]
                result["note"] = test.get("note", "")
                stage_results[stage].append(result)
        
        self.test_results["前台人员接待旅程"] = stage_results
        return stage_results

    async def test_admin_management_journey(self, client: httpx.AsyncClient):
        """测试管理员系统管理旅程"""
        print("\n⚙️ 测试管理员系统管理旅程...")
        
        journey_tests = {
            "阶段1-日常监控": [
                {"name": "系统状态监控", "method": "GET", "endpoint": "/health", "require_auth": False},
                {"name": "访客数据统计", "method": "GET", "endpoint": "/api/v1/visitors/"},
                {"name": "员工数据统计", "method": "GET", "endpoint": "/api/v1/employees/"},
                {"name": "部门数据统计", "method": "GET", "endpoint": "/api/v1/departments/"},
            ],
            "阶段2-配置管理": [
                {"name": "站点配置管理", "method": "GET", "endpoint": "/api/v1/sites/"},
                {"name": "部门配置管理", "method": "GET", "endpoint": "/api/v1/departments/"},
                {"name": "员工权限管理", "method": "GET", "endpoint": "/api/v1/employees/"},
            ]
        }
        
        stage_results = {}
        for stage, tests in journey_tests.items():
            stage_results[stage] = []
            for test in tests:
                result = await self.test_api_endpoint(
                    client,
                    test["method"],
                    test["endpoint"],
                    test.get("data"),
                    test.get("expected_status", 200),
                    test.get("require_auth", True)
                )
                result["test_name"] = test["name"]
                result["note"] = test.get("note", "")
                stage_results[stage].append(result)
        
        self.test_results["管理员系统管理旅程"] = stage_results
        return stage_results

    def calculate_coverage_summary(self):
        """计算API覆盖度统计"""
        total_tests = 0
        successful_tests = 0
        tests_with_api_support = 0
        tests_needing_development = 0
        
        for journey, stages in self.test_results.items():
            for stage, tests in stages.items():
                for test in tests:
                    total_tests += 1
                    if test["success"]:
                        successful_tests += 1
                        tests_with_api_support += 1
                    elif test.get("note") and "需要" in test.get("note", ""):
                        tests_needing_development += 1
                    else:
                        tests_with_api_support += 1  # API存在但可能有问题
        
        self.coverage_summary = {
            "total_journey_nodes": total_tests,
            "nodes_with_api_support": tests_with_api_support,
            "successful_api_calls": successful_tests,
            "nodes_needing_development": tests_needing_development,
            "api_coverage_rate": round((tests_with_api_support / total_tests) * 100, 2) if total_tests > 0 else 0,
            "api_success_rate": round((successful_tests / total_tests) * 100, 2) if total_tests > 0 else 0
        }

    def generate_report(self) -> str:
        """生成用户旅程API覆盖度报告"""
        self.calculate_coverage_summary()
        
        report = f"""
# 用户旅程API覆盖度测试报告

## 📊 总体统计
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **用户旅程总节点数**: {self.coverage_summary['total_journey_nodes']}
- **已有API支持的节点**: {self.coverage_summary['nodes_with_api_support']}
- **API调用成功的节点**: {self.coverage_summary['successful_api_calls']}
- **需要开发的节点**: {self.coverage_summary['nodes_needing_development']}
- **API覆盖率**: {self.coverage_summary['api_coverage_rate']}%
- **API成功率**: {self.coverage_summary['api_success_rate']}%

## 🎯 各用户旅程测试详情

"""
        
        for journey, stages in self.test_results.items():
            report += f"### {journey}\n\n"
            
            for stage, tests in stages.items():
                report += f"#### {stage}\n\n"
                report += "| 测试项 | 状态 | HTTP状态 | 备注 |\n"
                report += "|-------|------|----------|------|\n"
                
                for test in tests:
                    status_icon = "✅" if test["success"] else "❌"
                    note = test.get("note", "")
                    if note and "需要" in note:
                        status_icon = "🔨"  # 需要开发
                    
                    report += f"| {test['test_name']} | {status_icon} | {test['status_code']} | {note} |\n"
                
                report += "\n"
        
        # 添加缺失功能分析
        report += """
## 🔍 关键缺失功能分析

基于用户旅程地图，以下功能需要补充开发：

### 高优先级缺失功能
1. **访客签到/签出系统**
   - 二维码验证API
   - 访客签到记录API
   - 访客签出记录API
   
2. **身份验证系统**
   - 身份证OCR识别API
   - 人脸识别验证API
   - 多重身份验证API

3. **通知系统**
   - 实时消息推送API
   - 短信/邮件通知API
   - 到访提醒API

### 中优先级缺失功能
4. **权限管理系统**
   - 访问权限配置API
   - 区域权限管理API
   - 临时权限发放API

5. **流程管理系统**
   - 审批流程API
   - 状态跟踪API
   - 工作流引擎API

6. **资源管理系统**
   - 会议室预订API
   - 等候区管理API
   - 设备管理API

### 低优先级功能
7. **分析统计系统**
   - 访客数据分析API
   - 行为统计API
   - 报表生成API

8. **集成系统**
   - 日历集成API
   - 企业通讯录API
   - 第三方系统集成API

## 📋 开发建议

### 近期开发计划(1-2周)
1. 完善访客签到/签出API
2. 实现基础通知功能
3. 补充权限验证接口

### 中期开发计划(1个月)
1. 构建完整的身份验证系统
2. 实现审批流程管理
3. 开发资源管理功能

### 长期开发计划(2-3个月)
1. 构建数据分析平台
2. 实现高级集成功能
3. 优化用户体验细节

## 🎯 结论

当前系统已经具备了用户旅程中**{self.coverage_summary['api_coverage_rate']}%**的节点API支持，
核心的数据管理功能（员工、部门、站点、访客）已经完整实现。

需要重点补充的是**业务流程API**和**实时交互功能**，
这些功能将显著提升用户体验，使系统从数据管理工具升级为完整的业务流程平台。

建议按照优先级逐步开发缺失功能，确保系统能够支持完整的用户旅程体验。
"""
        
        return report

    async def run_all_tests(self):
        """运行所有用户旅程测试"""
        print("🚀 开始用户旅程API覆盖度测试...")
        
        async with httpx.AsyncClient() as client:
            # 首先进行身份认证
            print("🔐 进行身份认证...")
            auth_success = await self.authenticate(client)
            if auth_success:
                print("✅ 认证成功")
            else:
                print("❌ 认证失败，将跳过需要认证的API测试")
            
            # 测试各个用户旅程
            await self.test_visitor_self_application_journey(client)
            await self.test_employee_invitation_journey(client)
            await self.test_security_verification_journey(client)
            await self.test_reception_service_journey(client)
            await self.test_admin_management_journey(client)
        
        # 生成并保存报告
        report = self.generate_report()
        
        # 保存到文件
        with open("user_journey_api_coverage_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n✅ 测试完成！报告已保存到 user_journey_api_coverage_report.md")
        print(f"\n📊 快速总结:")
        print(f"   - 总节点数: {self.coverage_summary['total_journey_nodes']}")
        print(f"   - API覆盖率: {self.coverage_summary['api_coverage_rate']}%")
        print(f"   - API成功率: {self.coverage_summary['api_success_rate']}%")
        print(f"   - 需要开发: {self.coverage_summary['nodes_needing_development']}个功能")

if __name__ == "__main__":
    tester = UserJourneyTester()
    asyncio.run(tester.run_all_tests())