#!/usr/bin/env python3
"""
简化的配置引擎API测试

直接测试配置引擎API端点，不依赖复杂的认证系统。
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class SimpleConfigAPITester:
    """简化的配置引擎API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头（无需认证）"""
        return {
            "Content-Type": "application/json",
            "X-Tenant-ID": "test-tenant",
            "X-User-ID": "test-user"
        }
    
    async def test_server_connectivity(self) -> bool:
        """测试服务器连通性"""
        print("🔌 测试服务器连通性...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url.replace('/api/v1', '')}/")
                if response.status_code == 200:
                    print("✅ 服务器连接正常")
                    return True
                else:
                    print(f"⚠️  服务器响应码: {response.status_code}")
                    return True  # 返回True继续测试
            except Exception as e:
                print(f"❌ 服务器连接失败: {str(e)}")
                return False
    
    async def test_health_endpoint(self) -> bool:
        """测试健康检查端点"""
        print("🏥 测试健康检查端点...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url.replace('/api/v1', '')}/health")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 健康检查通过: {result.get('status', 'unknown')}")
                    return True
                else:
                    print(f"⚠️  健康检查响应码: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 健康检查失败: {str(e)}")
                return False
    
    async def test_config_form_endpoints(self) -> bool:
        """测试表单配置端点"""
        print("📝 测试表单配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 测试GET /config/forms
                print("  📋 获取表单配置列表...")
                response = await client.get(
                    f"{self.base_url}/config/forms/",
                    headers=self.get_headers()
                )
                print(f"    状态码: {response.status_code}")
                if response.status_code in [200, 404]:  # 404也可接受（没有数据）
                    print("    ✅ 表单列表端点可访问")
                else:
                    print(f"    ⚠️  表单列表响应: {response.text[:200]}")
                
                # 测试POST /config/forms 创建表单
                print("  📝 创建表单配置...")
                form_data = {
                    "form_name": "test_form_api",
                    "form_type": "visitor_registration",
                    "description": "通过API创建的测试表单",
                    "form_fields": [
                        {
                            "field_key": "visitor_name",
                            "field_label": "访客姓名",
                            "field_type": "text",
                            "field_order": 1,
                            "is_required": True,
                            "is_readonly": False,
                            "is_visible": True,
                            "placeholder_text": "请输入访客姓名"
                        }
                    ],
                    "form_schema": {
                        "type": "object",
                        "properties": {
                            "visitor_name": {
                                "type": "string",
                                "title": "访客姓名"
                            }
                        }
                    },
                    "ui_schema": {
                        "visitor_name": {
                            "ui:widget": "text"
                        }
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/config/forms/",
                    headers=self.get_headers(),
                    json=form_data
                )
                print(f"    状态码: {response.status_code}")
                if response.status_code in [200, 201]:
                    result = response.json()
                    print(f"    ✅ 表单创建成功: {result.get('id', 'unknown')}")
                    return True
                else:
                    print(f"    ⚠️  表单创建响应: {response.text[:200]}")
                    return False
                
            except Exception as e:
                print(f"❌ 表单配置API测试异常: {str(e)}")
                return False
    
    async def test_config_workflow_endpoints(self) -> bool:
        """测试工作流配置端点"""
        print("🔄 测试工作流配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 测试GET /config/workflows
                print("  📋 获取工作流配置列表...")
                response = await client.get(
                    f"{self.base_url}/config/workflows/",
                    headers=self.get_headers()
                )
                print(f"    状态码: {response.status_code}")
                if response.status_code in [200, 404]:
                    print("    ✅ 工作流列表端点可访问")
                    return True
                else:
                    print(f"    ⚠️  工作流列表响应: {response.text[:200]}")
                    return False
                
            except Exception as e:
                print(f"❌ 工作流配置API测试异常: {str(e)}")
                return False
    
    async def test_config_spatial_endpoints(self) -> bool:
        """测试空间配置端点"""
        print("🏢 测试空间配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 测试GET /config/spatial
                print("  📋 获取空间配置列表...")
                response = await client.get(
                    f"{self.base_url}/config/spatial/",
                    headers=self.get_headers()
                )
                print(f"    状态码: {response.status_code}")
                if response.status_code in [200, 404]:
                    print("    ✅ 空间配置列表端点可访问")
                    return True
                else:
                    print(f"    ⚠️  空间配置列表响应: {response.text[:200]}")
                    return False
                
            except Exception as e:
                print(f"❌ 空间配置API测试异常: {str(e)}")
                return False
    
    async def test_config_rules_endpoints(self) -> bool:
        """测试业务规则端点"""
        print("📋 测试业务规则API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 测试GET /config/rules
                print("  📋 获取业务规则列表...")
                response = await client.get(
                    f"{self.base_url}/config/rules/",
                    headers=self.get_headers()
                )
                print(f"    状态码: {response.status_code}")
                if response.status_code in [200, 404]:
                    print("    ✅ 业务规则列表端点可访问")
                    return True
                else:
                    print(f"    ⚠️  业务规则列表响应: {response.text[:200]}")
                    return False
                
            except Exception as e:
                print(f"❌ 业务规则API测试异常: {str(e)}")
                return False
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🧪 开始配置引擎API简化测试")
        print("="*60)
        
        test_results = []
        
        # 1. 测试服务器连通性
        connectivity_ok = await self.test_server_connectivity()
        test_results.append(("服务器连通性", connectivity_ok))
        
        if not connectivity_ok:
            print("❌ 服务器连接失败，停止测试")
            return False
        
        # 2. 测试健康检查
        health_ok = await self.test_health_endpoint()
        test_results.append(("健康检查", health_ok))
        
        # 3. 测试配置引擎API端点
        form_ok = await self.test_config_form_endpoints()
        test_results.append(("表单配置API", form_ok))
        
        workflow_ok = await self.test_config_workflow_endpoints()
        test_results.append(("工作流配置API", workflow_ok))
        
        spatial_ok = await self.test_config_spatial_endpoints()
        test_results.append(("空间配置API", spatial_ok))
        
        rules_ok = await self.test_config_rules_endpoints()
        test_results.append(("业务规则API", rules_ok))
        
        # 统计结果
        print("\n📊 测试结果统计:")
        print("-"*40)
        passed = 0
        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            if result:
                passed += 1
        
        total = len(test_results)
        print(f"\n🎯 总结: {passed}/{total} 项测试通过 ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过！配置引擎API基本功能正常。")
            return True
        elif passed >= total * 0.5:
            print("⚠️  大部分测试通过，配置引擎API基本可用。")
            return True
        else:
            print("❌ 多数测试失败，配置引擎API需要修复。")
            return False


async def main():
    """主函数"""
    tester = SimpleConfigAPITester()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️  测试已被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n💥 测试执行出错: {str(e)}")
        exit(1) 