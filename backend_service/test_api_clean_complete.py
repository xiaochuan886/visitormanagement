#!/usr/bin/env python3
"""
配置引擎API完整测试 - 包含数据清理功能
"""
import requests
import json
import random
import string
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def generate_random_suffix(length=8):
    """生成随机后缀"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_api_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """测试API端点的通用函数"""
    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return {"error": f"不支持的HTTP方法: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "data": response.json() if response.content else None,
            "error": None
        }
    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "success": False,
            "data": None,
            "error": str(e)
        }

def test_server_health():
    """测试服务器健康状态"""
    print("🏥 测试健康检查端点...")
    result = test_api_endpoint(f"{BASE_URL}/health")
    
    if result["success"]:
        print(f"✅ 健康检查通过: {result['data'].get('status', '未知')}")
        return True
    else:
        print(f"❌ 健康检查失败: {result['error']}")
        return False

def clean_test_data():
    """清理已有的测试数据"""
    print("🧹 清理测试数据...")
    
    # 获取现有表单列表
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/forms/")
    
    if not result["success"]:
        print("⚠️ 无法获取表单列表进行清理")
        return
    
    forms = result["data"]
    if not forms:
        print("✅ 没有需要清理的数据")
        return
    
    # 删除测试表单
    deleted_count = 0
    for form in forms:
        if "API测试表单" in form.get("form_name", ""):
            form_id = form["id"]
            delete_result = test_api_endpoint(f"{BASE_URL}/api/v1/config/forms/{form_id}", method="DELETE")
            if delete_result["success"]:
                deleted_count += 1
                print(f"  ✅ 删除表单: {form['form_name']}")
            else:
                print(f"  ⚠️ 删除失败: {form['form_name']} - {delete_result.get('error', '未知错误')}")
    
    print(f"✅ 清理完成，删除了 {deleted_count} 个测试表单")

def test_form_api():
    """测试表单配置API"""
    print("📝 测试表单配置API...")
    
    # 1. 获取表单配置列表
    print("  📋 获取表单配置列表...")
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/forms/")
    
    if result["success"]:
        print(f"    状态码: {result['status_code']}")
        print("    ✅ 表单列表端点可访问")
        forms = result["data"]
        print(f"    📊 当前表单数量: {len(forms)}")
    else:
        print(f"    ❌ 表单列表失败: {result['error']}")
        return False
    
    # 2. 创建表单配置
    print("  📝 创建表单配置...")
    suffix = generate_random_suffix()
    
    form_data = {
        "form_name": f"API测试表单_{suffix}",
        "form_type": "department_form",
        "description": "通过API创建的测试表单",
        "is_default": False,
        "form_fields": [
            {
                "field_key": "department_name",
                "field_label": "部门名称",
                "field_type": "text",
                "field_order": 1,
                "is_required": True,
                "is_readonly": False,
                "is_visible": True,
                "placeholder_text": "请输入部门名称"
            },
            {
                "field_key": "department_manager",
                "field_label": "部门经理",
                "field_type": "text",
                "field_order": 2,
                "is_required": False,
                "is_readonly": False,
                "is_visible": True,
                "placeholder_text": "请输入部门经理姓名"
            }
        ]
    }
    
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/forms/", method="POST", data=form_data)
    
    if result["success"]:
        print(f"    状态码: {result['status_code']}")
        print("    ✅ 表单创建成功")
        created_form = result["data"]
        print(f"    📄 创建的表单ID: {created_form.get('id')}")
        print(f"    📄 表单名称: {created_form.get('form_name')}")
        print(f"    📄 表单类型: {created_form.get('form_type')}")
        print(f"    📄 字段数量: {len(created_form.get('form_fields', []))}")
        
        # 验证返回的必需字段
        required_fields = ['id', 'form_name', 'form_type', 'form_version', 'is_default', 
                          'form_fields', 'tenant_id', 'updated_at']
        missing_fields = [field for field in required_fields if field not in created_form]
        
        if missing_fields:
            print(f"    ⚠️ 缺少必需字段: {missing_fields}")
        else:
            print("    ✅ 所有必需字段都存在")
        
        return True, created_form["id"]
    else:
        print(f"    ❌ 表单创建失败")
        if result["data"]:
            print(f"    错误详情: {result['data']}")
        return False, None

def test_workflow_api():
    """测试工作流配置API"""
    print("🔄 测试工作流配置API...")
    
    print("  📋 获取工作流配置列表...")
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/workflows/")
    
    if result["success"]:
        print(f"    状态码: {result['status_code']}")
        print("    ✅ 工作流列表端点可访问")
        return True
    else:
        print(f"    ❌ 工作流列表失败: {result['error']}")
        return False

def test_spatial_api():
    """测试空间配置API"""
    print("🏢 测试空间配置API...")
    
    print("  📋 获取空间配置列表...")
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/spatial/")
    
    if result["success"]:
        print(f"    状态码: {result['status_code']}")
        print("    ✅ 空间配置列表端点可访问")
        return True
    else:
        print(f"    ❌ 空间配置列表失败: {result['error']}")
        return False

def test_business_rules_api():
    """测试业务规则API"""
    print("📋 测试业务规则API...")
    
    print("  📋 获取业务规则列表...")
    result = test_api_endpoint(f"{BASE_URL}/api/v1/config/rules/")
    
    if result["success"]:
        print(f"    状态码: {result['status_code']}")
        print("    ✅ 业务规则列表端点可访问")
        return True
    else:
        print(f"    ❌ 业务规则列表失败: {result['error']}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始配置引擎API完整测试")
    print("=" * 60)
    
    # 测试服务器连通性
    print("🔌 测试服务器连通性...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ 服务器连接正常")
    except requests.exceptions.RequestException as e:
        print(f"❌ 服务器连接失败: {e}")
        return
    
    # 测试健康检查
    health_ok = test_server_health()
    if not health_ok:
        print("❌ 健康检查失败，停止测试")
        return
    
    # 清理测试数据
    clean_test_data()
    
    # 测试各个API
    results = {}
    
    form_ok, form_id = test_form_api()
    results["表单配置API"] = form_ok
    
    workflow_ok = test_workflow_api()
    results["工作流配置API"] = workflow_ok
    
    spatial_ok = test_spatial_api()
    results["空间配置API"] = spatial_ok
    
    rules_ok = test_business_rules_api()
    results["业务规则API"] = rules_ok
    
    # 统计结果
    print("\n📊 测试结果统计:")
    print("-" * 40)
    print(f"  服务器连通性: {'✅ 通过' if True else '❌ 失败'}")
    print(f"  健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    
    for api_name, result in results.items():
        print(f"  {api_name}: {'✅ 通过' if result else '❌ 失败'}")
    
    # 计算通过率
    total_tests = len(results) + 2  # +2 for connectivity and health
    passed_tests = sum([1 for r in results.values() if r]) + 2  # +2 for connectivity and health
    pass_rate = (passed_tests / total_tests) * 100
    
    print(f"\n🎯 总结: {passed_tests}/{total_tests} 项测试通过 ({pass_rate:.1f}%)")
    
    if pass_rate == 100:
        print("🎉 所有测试通过！配置引擎API完全可用。")
    elif pass_rate >= 80:
        print("✅ 大部分测试通过，配置引擎API基本可用。")
    elif pass_rate >= 50:
        print("⚠️ 部分测试通过，需要进一步调试。")
    else:
        print("❌ 多数测试失败，需要检查系统配置。")

if __name__ == "__main__":
    main() 