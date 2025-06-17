#!/usr/bin/env python3
"""
访客管理系统配置引擎集成测试脚本
测试表单、工作流、空间、业务规则等4个核心模块的API功能
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ConfigEngineAPITester:
    """配置引擎API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.auth_token: Optional[str] = None
        self.tenant_id = "test-tenant"
        
    async def authenticate(self) -> bool:
        """认证获取Token"""
        print("🔐 开始用户认证...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 使用已有的测试用户进行认证
                auth_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                response = await client.post(
                    f"{self.base_url}/auth/login",
                    json=auth_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.auth_token = result.get("access_token")
                    print(f"✅ 认证成功，获取Token: {self.auth_token[:20]}...")
                    return True
                else:
                    print(f"❌ 认证失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ 认证异常: {str(e)}")
                return False

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }

    async def test_form_configuration_api(self) -> bool:
        """测试表单配置API"""
        print("\n📝 测试表单配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. 创建表单配置
                form_config_data = {
                    "config_name": "测试访客登记表单",
                    "form_type": "visitor_registration",
                    "description": "测试用访客登记表单配置",
                    "fields": [
                        {
                            "field_name": "visitor_name",
                            "field_type": "text",
                            "label": "访客姓名",
                            "required": True,
                            "validation_rules": {
                                "min_length": 2,
                                "max_length": 50
                            }
                        },
                        {
                            "field_name": "phone",
                            "field_type": "tel",
                            "label": "联系电话",
                            "required": True,
                            "validation_rules": {
                                "pattern": "^1[3-9]\\d{9}$"
                            }
                        },
                        {
                            "field_name": "visit_purpose",
                            "field_type": "select",
                            "label": "来访目的",
                            "required": True,
                            "options": [
                                {"value": "business", "label": "商务洽谈"},
                                {"value": "interview", "label": "面试"},
                                {"value": "meeting", "label": "会议"}
                            ]
                        }
                    ],
                    "ui_schema": {
                        "layout": "vertical",
                        "submit_button_text": "提交登记",
                        "theme": "default"
                    },
                    "validation_schema": {
                        "required_fields": ["visitor_name", "phone", "visit_purpose"],
                        "conditional_rules": []
                    }
                }
                
                print("  📤 创建表单配置...")
                response = await client.post(
                    f"{self.base_url}/config/forms",
                    headers=self.get_headers(),
                    json=form_config_data
                )
                
                if response.status_code == 201:
                    form_config = response.json()
                    form_id = form_config["id"]
                    print(f"  ✅ 表单配置创建成功: {form_id}")
                    
                    # 2. 获取表单配置列表
                    print("  📋 获取表单配置列表...")
                    response = await client.get(
                        f"{self.base_url}/config/forms",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        configs = response.json()
                        print(f"  ✅ 获取配置列表成功，共 {len(configs)} 个配置")
                    else:
                        print(f"  ❌ 获取配置列表失败: {response.status_code}")
                        return False
                    
                    # 3. 获取表单渲染数据
                    print("  🎨 获取表单渲染数据...")
                    response = await client.get(
                        f"{self.base_url}/config/forms/{form_id}/render",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        render_data = response.json()
                        print(f"  ✅ 获取渲染数据成功，包含 {len(render_data.get('fields', []))} 个字段")
                    else:
                        print(f"  ❌ 获取渲染数据失败: {response.status_code}")
                        return False
                    
                    # 4. 验证表单数据
                    print("  🔍 验证表单数据...")
                    test_form_data = {
                        "visitor_name": "张三",
                        "phone": "13812345678", 
                        "visit_purpose": "business"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/config/forms/{form_id}/validate",
                        headers=self.get_headers(),
                        json=test_form_data
                    )
                    
                    if response.status_code == 200:
                        validation_result = response.json()
                        print(f"  ✅ 表单验证成功: {validation_result.get('is_valid', False)}")
                    else:
                        print(f"  ❌ 表单验证失败: {response.status_code}")
                        return False
                    
                    return True
                    
                else:
                    print(f"  ❌ 创建表单配置失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 表单配置API测试异常: {str(e)}")
                return False

    async def test_workflow_configuration_api(self) -> bool:
        """测试工作流配置API"""
        print("\n🔄 测试工作流配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. 创建工作流配置
                workflow_config_data = {
                    "workflow_name": "测试访客审批工作流",
                    "workflow_type": "visitor_approval",
                    "description": "测试用访客审批流程",
                    "trigger_conditions": {
                        "form_type": "visitor_registration",
                        "visit_purpose": ["business", "meeting"]
                    },
                    "steps": [
                        {
                            "step_name": "部门审批",
                            "step_type": "manual_approval",
                            "step_order": 1,
                            "assignee_type": "department_manager",
                            "timeout_minutes": 1440,
                            "auto_approval_rules": {
                                "conditions": [],
                                "enabled": False
                            }
                        },
                        {
                            "step_name": "安保审批",
                            "step_type": "manual_approval",
                            "step_order": 2,
                            "assignee_type": "security_officer", 
                            "timeout_minutes": 720
                        },
                        {
                            "step_name": "发送通知",
                            "step_type": "notification",
                            "step_order": 3,
                            "notification_config": {
                                "channels": ["sms", "email"],
                                "templates": {
                                    "sms": "您的访客申请已通过审批",
                                    "email": "访客申请审批通知"
                                }
                            }
                        }
                    ],
                    "failure_handling": {
                        "retry_count": 3,
                        "retry_interval_minutes": 30
                    }
                }
                
                print("  📤 创建工作流配置...")
                response = await client.post(
                    f"{self.base_url}/config/workflows",
                    headers=self.get_headers(),
                    json=workflow_config_data
                )
                
                if response.status_code == 201:
                    workflow_config = response.json()
                    workflow_id = workflow_config["id"]
                    print(f"  ✅ 工作流配置创建成功: {workflow_id}")
                    
                    # 2. 获取工作流配置详情
                    print("  📋 获取工作流配置详情...")
                    response = await client.get(
                        f"{self.base_url}/config/workflows/{workflow_id}",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        config_detail = response.json()
                        print(f"  ✅ 获取配置详情成功，包含 {len(config_detail.get('steps', []))} 个步骤")
                    else:
                        print(f"  ❌ 获取配置详情失败: {response.status_code}")
                        return False
                    
                    # 3. 启动工作流执行
                    print("  🚀 启动工作流执行...")
                    execution_data = {
                        "context_data": {
                            "visitor_id": "test-visitor-id",
                            "form_data": {
                                "visitor_name": "张三",
                                "phone": "13812345678",
                                "visit_purpose": "business"
                            }
                        },
                        "priority": "normal"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/config/workflows/{workflow_id}/execute",
                        headers=self.get_headers(),
                        json=execution_data
                    )
                    
                    if response.status_code == 201:
                        execution_result = response.json()
                        execution_id = execution_result["id"]
                        print(f"  ✅ 工作流执行启动成功: {execution_id}")
                    else:
                        print(f"  ❌ 工作流执行启动失败: {response.status_code}")
                        return False
                    
                    return True
                    
                else:
                    print(f"  ❌ 创建工作流配置失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 工作流配置API测试异常: {str(e)}")
                return False

    async def test_spatial_configuration_api(self) -> bool:
        """测试空间配置API"""
        print("\n🏢 测试空间配置API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. 创建空间配置
                spatial_config_data = {
                    "config_name": "测试总部大厦空间配置",
                    "description": "测试用总部大厦完整空间层级管理",
                    "hierarchy_levels": [
                        {"level": 1, "type": "site", "name": "站点"},
                        {"level": 2, "type": "building", "name": "楼栋"},
                        {"level": 3, "type": "floor", "name": "楼层"},
                        {"level": 4, "type": "zone", "name": "区域"},
                        {"level": 5, "type": "room", "name": "房间"}
                    ],
                    "access_control_rules": {
                        "default_access_level": "restricted",
                        "visitor_accessible_types": ["room", "meeting_room"],
                        "requires_escort": ["server_room", "finance_area"]
                    }
                }
                
                print("  📤 创建空间配置...")
                response = await client.post(
                    f"{self.base_url}/config/spatial",
                    headers=self.get_headers(),
                    json=spatial_config_data
                )
                
                if response.status_code == 201:
                    spatial_config = response.json()
                    config_id = spatial_config["id"]
                    print(f"  ✅ 空间配置创建成功: {config_id}")
                    
                    # 2. 创建空间实体
                    print("  🏠 创建空间实体...")
                    entity_data = {
                        "entity_code": "HQ-B1-F1-001",
                        "entity_name": "测试会议室A",
                        "entity_type": "room",
                        "parent_id": None,  # 根级空间
                        "capacity": 12,
                        "area_sqm": 25.5,
                        "coordinates": {
                            "latitude": 39.908722,
                            "longitude": 116.397496
                        },
                        "facilities": [
                            "projector",
                            "whiteboard",
                            "video_conference"
                        ],
                        "access_devices": [
                            {
                                "device_id": "door-001",
                                "device_type": "door_controller",
                                "device_name": "会议室A门禁"
                            }
                        ],
                        "operating_hours": {
                            "weekdays": {
                                "start": "08:00",
                                "end": "18:00"
                            },
                            "weekends": {
                                "start": "09:00",
                                "end": "17:00"
                            }
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/config/spatial/{config_id}/entities",
                        headers=self.get_headers(),
                        json=entity_data
                    )
                    
                    if response.status_code == 201:
                        entity = response.json()
                        entity_id = entity["id"]
                        print(f"  ✅ 空间实体创建成功: {entity_id}")
                    else:
                        print(f"  ❌ 空间实体创建失败: {response.status_code}")
                        return False
                    
                    # 3. 获取空间层级结构
                    print("  🌲 获取空间层级结构...")
                    response = await client.get(
                        f"{self.base_url}/config/spatial/{config_id}/hierarchy",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        hierarchy = response.json()
                        print(f"  ✅ 获取层级结构成功")
                    else:
                        print(f"  ❌ 获取层级结构失败: {response.status_code}")
                        return False
                    
                    # 4. 搜索空间实体
                    print("  🔍 搜索空间实体...")
                    response = await client.get(
                        f"{self.base_url}/config/spatial/search?query=会议室&limit=10",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        search_results = response.json()
                        print(f"  ✅ 搜索完成，找到 {len(search_results)} 个结果")
                    else:
                        print(f"  ❌ 搜索失败: {response.status_code}")
                        return False
                    
                    return True
                    
                else:
                    print(f"  ❌ 创建空间配置失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 空间配置API测试异常: {str(e)}")
                return False

    async def test_business_rules_api(self) -> bool:
        """测试业务规则API"""
        print("\n⚡ 测试业务规则API...")
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. 创建业务规则
                rule_data = {
                    "rule_name": "测试VIP访客自动审批",
                    "rule_type": "validation_rule",
                    "rule_category": "auto_approval",
                    "description": "测试用VIP客户访客申请自动审批规则",
                    "conditions": {
                        "operator": "AND",
                        "rules": [
                            {
                                "field": "visitor_company",
                                "operator": "in",
                                "value": ["重要客户A", "重要客户B", "重要客户C"]
                            },
                            {
                                "field": "visit_purpose",
                                "operator": "equals",
                                "value": "business"
                            },
                            {
                                "field": "visit_time",
                                "operator": "between",
                                "value": ["09:00", "17:00"]
                            }
                        ]
                    },
                    "actions": [
                        {
                            "action_type": "auto_approve",
                            "parameters": {
                                "approval_level": "department",
                                "skip_security_check": False
                            }
                        },
                        {
                            "action_type": "send_notification",
                            "parameters": {
                                "recipients": ["security@company.com"],
                                "template": "vip_visitor_auto_approved"
                            }
                        }
                    ],
                    "priority": 90,
                    "execution_order": 1
                }
                
                print("  📤 创建业务规则...")
                response = await client.post(
                    f"{self.base_url}/config/rules",
                    headers=self.get_headers(),
                    json=rule_data
                )
                
                if response.status_code == 201:
                    rule = response.json()
                    rule_id = rule["id"]
                    print(f"  ✅ 业务规则创建成功: {rule_id}")
                    
                    # 2. 获取业务规则详情
                    print("  📋 获取业务规则详情...")
                    response = await client.get(
                        f"{self.base_url}/config/rules/{rule_id}",
                        headers=self.get_headers()
                    )
                    
                    if response.status_code == 200:
                        rule_detail = response.json()
                        print(f"  ✅ 获取规则详情成功")
                    else:
                        print(f"  ❌ 获取规则详情失败: {response.status_code}")
                        return False
                    
                    # 3. 执行业务规则
                    print("  🚀 执行业务规则...")
                    execution_data = {
                        "input_data": {
                            "visitor_company": "重要客户A",
                            "visit_purpose": "business",
                            "visit_time": "14:30",
                            "visitor_name": "李总",
                            "phone": "13987654321"
                        },
                        "execution_context": {
                            "visitor_id": "test-visitor-id",
                            "form_submission_id": "test-form-id"
                        }
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/config/rules/{rule_id}/execute",
                        headers=self.get_headers(),
                        json=execution_data
                    )
                    
                    if response.status_code == 200:
                        execution_result = response.json()
                        print(f"  ✅ 规则执行成功: {execution_result.get('execution_result', 'unknown')}")
                    else:
                        print(f"  ❌ 规则执行失败: {response.status_code}")
                        return False
                    
                    # 4. 验证业务规则
                    print("  🔍 验证业务规则...")
                    test_data = {
                        "visitor_company": "测试客户",
                        "visit_purpose": "meeting"
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/config/rules/{rule_id}/validate",
                        headers=self.get_headers(),
                        json=test_data
                    )
                    
                    if response.status_code == 200:
                        validation_result = response.json()
                        print(f"  ✅ 规则验证完成")
                    else:
                        print(f"  ❌ 规则验证失败: {response.status_code}")
                        return False
                    
                    return True
                    
                else:
                    print(f"  ❌ 创建业务规则失败: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"  ❌ 业务规则API测试异常: {str(e)}")
                return False

    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🧪 开始配置引擎API全面测试")
        print("=" * 60)
        
        # 1. 认证
        if not await self.authenticate():
            print("❌ 认证失败，测试终止")
            return False
        
        # 2. 测试各模块API
        test_results = {}
        
        test_results["form_config"] = await self.test_form_configuration_api()
        test_results["workflow_config"] = await self.test_workflow_configuration_api()
        test_results["spatial_config"] = await self.test_spatial_configuration_api()
        test_results["business_rules"] = await self.test_business_rules_api()
        
        # 3. 输出测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果汇总:")
        print("=" * 60)
        
        all_passed = True
        for module, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {module:20} : {status}")
            if not result:
                all_passed = False
        
        print("=" * 60)
        if all_passed:
            print("🎉 所有测试通过！配置引擎API功能正常")
        else:
            print("⚠️  部分测试失败，请检查相关模块")
        
        return all_passed

async def main():
    """主函数"""
    tester = ConfigEngineAPITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 配置引擎已准备就绪！")
        return 0
    else:
        print("\n🔧 需要修复发现的问题")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 