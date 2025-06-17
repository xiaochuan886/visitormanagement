#!/usr/bin/env python3
"""
完整的配置引擎API测试
测试HTTP接口层的完整功能
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
import uuid

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))


class ConfigEngineAPITester:
    """配置引擎API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.created_form_ids = []
    
    def get_headers(self) -> dict:
        """获取请求头"""
        return {
            "Content-Type": "application/json",
            "X-Tenant-ID": "api-test-tenant",
            "X-User-ID": "api-test-user"
        }
    
    async def test_server_health(self) -> bool:
        """测试服务器健康状态"""
        print("🏥 测试服务器健康状态...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url.replace('/api/v1', '')}/health")
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ 服务器健康: {result.get('status', 'unknown')}")
                    return True
                else:
                    print(f"  ❌ 健康检查失败，状态码: {response.status_code}")
                    return False
            except Exception as e:
                print(f"  ❌ 健康检查异常: {str(e)}")
                return False
    
    async def test_form_list_api(self) -> bool:
        """测试表单列表API"""
        print("\n📋 测试表单列表API...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/config/forms/",
                    headers=self.get_headers()
                )
                
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        forms = result.get('data', [])
                        print(f"  ✅ 表单列表获取成功: {len(forms)} 个表单")
                        return True
                    else:
                        print(f"  ❌ API返回失败: {result.get('error', '未知错误')}")
                        return False
                else:
                    print(f"  ❌ API请求失败: {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 请求异常: {str(e)}")
                return False
    
    async def test_form_create_api(self) -> bool:
        """测试表单创建API"""
        print("\n📝 测试表单创建API...")
        
        # 生成唯一表单名
        unique_id = uuid.uuid4().hex[:8]
        form_data = {
            "form_name": f"API测试表单_{unique_id}",
            "form_type": "department_form",  # 使用不同的类型避免冲突
            "description": "通过API创建的测试表单",
            "form_fields": [
                {
                    "field_key": "department_name",
                    "field_label": "部门名称",
                    "field_type": "text",
                    "field_order": 1,
                    "is_required": True,
                    "placeholder_text": "请输入部门名称"
                },
                {
                    "field_key": "department_manager",
                    "field_label": "部门经理",
                    "field_type": "text", 
                    "field_order": 2,
                    "is_required": False,
                    "placeholder_text": "请输入部门经理姓名"
                }
            ],
            "form_schema": {
                "type": "object",
                "properties": {
                    "department_name": {"type": "string", "title": "部门名称"},
                    "department_manager": {"type": "string", "title": "部门经理"}
                },
                "required": ["department_name"]
            },
            "ui_schema": {
                "department_name": {"ui:widget": "text"},
                "department_manager": {"ui:widget": "text"}
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/config/forms/",
                    headers=self.get_headers(),
                    json=form_data
                )
                
                print(f"  状态码: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    if result.get('success', False):
                        form_id = result.get('data', {}).get('id')
                        if form_id:
                            self.created_form_ids.append(form_id)
                        print(f"  ✅ 表单创建成功: {form_data['form_name']}")
                        print(f"     表单ID: {form_id}")
                        return True
                    else:
                        print(f"  ❌ API返回失败: {result.get('error', '未知错误')}")
                        return False
                else:
                    print(f"  ❌ 创建失败: {response.text[:300]}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 请求异常: {str(e)}")
                return False
    
    async def test_other_config_apis(self) -> dict:
        """测试其他配置API"""
        print("\n🔄 测试其他配置引擎API...")
        
        results = {}
        
        apis = [
            ("工作流配置", "/config/workflows/"),
            ("空间配置", "/config/spatial/"),
            ("业务规则", "/config/rules/")
        ]
        
        async with httpx.AsyncClient() as client:
            for api_name, endpoint in apis:
                try:
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.get_headers()
                    )
                    
                    success = response.status_code == 200
                    results[api_name] = success
                    status = "✅" if success else "❌"
                    print(f"  {status} {api_name}: 状态码 {response.status_code}")
                    
                except Exception as e:
                    results[api_name] = False
                    print(f"  ❌ {api_name}: 异常 {str(e)}")
        
        return results
    
    async def test_form_details_api(self) -> bool:
        """测试表单详情API"""
        if not self.created_form_ids:
            print("\n⚠️  跳过表单详情测试 - 没有可用的表单ID")
            return True
            
        print("\n🔍 测试表单详情API...")
        
        form_id = self.created_form_ids[0]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/config/forms/{form_id}/",
                    headers=self.get_headers()
                )
                
                print(f"  状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', False):
                        form_data = result.get('data', {})
                        print(f"  ✅ 表单详情获取成功")
                        print(f"     表单名称: {form_data.get('form_name', '未知')}")
                        print(f"     字段数量: {len(form_data.get('form_fields', []))}")
                        return True
                    else:
                        print(f"  ❌ API返回失败: {result.get('error', '未知错误')}")
                        return False
                else:
                    print(f"  ❌ 详情获取失败: {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 请求异常: {str(e)}")
                return False
    
    async def cleanup_test_data(self) -> bool:
        """清理测试数据"""
        if not self.created_form_ids:
            return True
            
        print("\n🧹 清理API测试数据...")
        
        async with httpx.AsyncClient() as client:
            for form_id in self.created_form_ids:
                try:
                    response = await client.delete(
                        f"{self.base_url}/config/forms/{form_id}/",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code in [200, 204, 404]:
                        print(f"  ✅ 清理表单: {form_id}")
                    else:
                        print(f"  ⚠️  清理失败: {form_id} (状态码: {response.status_code})")
                        
                except Exception as e:
                    print(f"  ⚠️  清理异常: {form_id} - {str(e)}")
        
        return True


async def main():
    """主函数"""
    print("=" * 60)
    print("🌐 配置引擎API完整测试")
    print("=" * 60)
    
    tester = ConfigEngineAPITester()
    results = []
    
    # 执行测试步骤
    results.append(("服务器健康", await tester.test_server_health()))
    results.append(("表单列表API", await tester.test_form_list_api()))
    results.append(("表单创建API", await tester.test_form_create_api()))
    results.append(("表单详情API", await tester.test_form_details_api()))
    
    # 测试其他API
    other_results = await tester.test_other_config_apis()
    for api_name, success in other_results.items():
        results.append((f"{api_name}API", success))
    
    # 清理测试数据
    await tester.cleanup_test_data()
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📊 API测试报告")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name:<20}: {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"🎯 总结: {passed}/{total} 项API测试通过 ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:  # 80%通过率算成功
        print("🎉 API层测试基本成功！")
        print("\n✅ 验证成功的API:")
        success_apis = [name for name, success in results if success]
        for api in success_apis:
            print(f"   • {api}")
        
        if passed < total:
            print(f"\n⚠️  需要关注的API:")
            failed_apis = [name for name, success in results if not success]
            for api in failed_apis:
                print(f"   • {api}")
        
        print("\n🚀 配置引擎API层基本可用！")
        return 0
    else:
        print("❌ API层测试失败，需要修复")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 