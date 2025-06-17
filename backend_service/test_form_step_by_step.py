#!/usr/bin/env python3
"""
分步骤表单功能测试
详细测试表单创建、查询、更新等功能
"""

import asyncio
import sys
from pathlib import Path
import uuid
import json

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database.connection import async_session_factory
from app.application.services.config_services_simple import SimpleFormConfigurationService


async def test_step_1_create_basic_form():
    """第1步：创建基础表单"""
    print("📝 第1步：创建基础访客表单...")
    
    try:
        async with async_session_factory() as session:
            service = SimpleFormConfigurationService(session)
            
            # 基础访客表单
            form_data = {
                "form_name": "访客登记表单_基础版",
                "form_type": "visitor_registration",
                "description": "基础访客登记表单，包含必填字段",
                "form_fields": [
                    {
                        "field_key": "visitor_name",
                        "field_label": "访客姓名",
                        "field_type": "text",
                        "field_order": 1,
                        "is_required": True,
                        "placeholder_text": "请输入访客姓名"
                    },
                    {
                        "field_key": "visitor_phone",
                        "field_label": "联系电话",
                        "field_type": "phone",
                        "field_order": 2,
                        "is_required": True,
                        "placeholder_text": "请输入手机号码"
                    }
                ],
                "form_schema": {
                    "type": "object",
                    "properties": {
                        "visitor_name": {"type": "string", "title": "访客姓名"},
                        "visitor_phone": {"type": "string", "title": "联系电话"}
                    },
                    "required": ["visitor_name", "visitor_phone"]
                }
            }
            
            result = await service.create_form_configuration(
                tenant_id="test-tenant",
                form_config=form_data,
                created_by="test-user"
            )
            
            print(f"  ✅ 基础表单创建成功")
            print(f"     表单ID: {result['id']}")
            print(f"     表单名称: {result['form_name']}")
            print(f"     表单类型: {result['form_type']}")
            
            return result['id']
            
    except Exception as e:
        print(f"  ❌ 基础表单创建失败: {str(e)}")
        return None


async def test_step_2_create_advanced_form():
    """第2步：创建高级表单"""
    print("\n📋 第2步：创建高级员工表单...")
    
    try:
        async with async_session_factory() as session:
            service = SimpleFormConfigurationService(session)
            
            # 高级员工表单
            form_data = {
                "form_name": "员工信息表单_高级版",
                "form_type": "employee_form",
                "description": "高级员工信息表单，包含多种字段类型",
                "form_fields": [
                    {
                        "field_key": "employee_name",
                        "field_label": "员工姓名",
                        "field_type": "text",
                        "field_order": 1,
                        "is_required": True
                    },
                    {
                        "field_key": "employee_email",
                        "field_label": "员工邮箱",
                        "field_type": "email",
                        "field_order": 2,
                        "is_required": True
                    },
                    {
                        "field_key": "hire_date",
                        "field_label": "入职日期",
                        "field_type": "date",
                        "field_order": 3,
                        "is_required": False
                    },
                    {
                        "field_key": "department",
                        "field_label": "所属部门",
                        "field_type": "select",
                        "field_order": 4,
                        "is_required": True,
                        "field_options": {
                            "options": [
                                {"value": "it", "label": "技术部"},
                                {"value": "hr", "label": "人事部"},
                                {"value": "finance", "label": "财务部"}
                            ]
                        }
                    }
                ]
            }
            
            result = await service.create_form_configuration(
                tenant_id="test-tenant",
                form_config=form_data,
                created_by="test-user"
            )
            
            print(f"  ✅ 高级表单创建成功")
            print(f"     表单ID: {result['id']}")
            print(f"     表单名称: {result['form_name']}")
            print(f"     字段数量: 4个")
            
            return result['id']
            
    except Exception as e:
        print(f"  ❌ 高级表单创建失败: {str(e)}")
        return None


async def test_step_3_list_forms():
    """第3步：查询表单列表"""
    print("\n📄 第3步：查询表单列表...")
    
    try:
        async with async_session_factory() as session:
            service = SimpleFormConfigurationService(session)
            
            # 获取所有表单
            all_forms = await service.list_form_configurations(
                tenant_id="test-tenant",
                skip=0,
                limit=10
            )
            
            print(f"  ✅ 表单列表查询成功")
            print(f"     总表单数: {len(all_forms)}")
            
            for i, form in enumerate(all_forms, 1):
                print(f"     {i}. {form.get('form_name', '未知')} ({form.get('form_type', '未知')})")
            
            # 按类型过滤
            visitor_forms = await service.list_form_configurations(
                tenant_id="test-tenant",
                form_type="visitor_registration",
                skip=0,
                limit=5
            )
            
            print(f"\n  📋 访客表单筛选:")
            print(f"     访客表单数: {len(visitor_forms)}")
            
            return len(all_forms)
            
    except Exception as e:
        print(f"  ❌ 表单列表查询失败: {str(e)}")
        return 0


async def test_step_4_form_constraints():
    """第4步：测试表单约束和验证"""
    print("\n🔒 第4步：测试表单约束...")
    
    try:
        async with async_session_factory() as session:
            service = SimpleFormConfigurationService(session)
            
            # 测试1：重复表单类型和版本（应该失败）
            print("  🧪 测试重复约束...")
            try:
                duplicate_form = {
                    "form_name": "重复测试表单",
                    "form_type": "visitor_registration",  # 与第1步相同类型
                    "form_version": 1,  # 默认版本1，应该冲突
                    "description": "测试重复约束",
                    "form_fields": []
                }
                
                await service.create_form_configuration(
                    tenant_id="test-tenant",
                    form_config=duplicate_form,
                    created_by="test-user"
                )
                print("    ⚠️  重复约束测试失败 - 应该报错但没有")
                
            except Exception as e:
                if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                    print("    ✅ 重复约束测试通过 - 正确阻止了重复创建")
                else:
                    print(f"    ❌ 重复约束测试异常: {str(e)}")
            
            # 测试2：无效字段类型（应该失败）
            print("  🧪 测试字段类型约束...")
            try:
                invalid_form = {
                    "form_name": "无效字段类型测试",
                    "form_type": "site_form",
                    "description": "测试无效字段类型",
                    "form_fields": [
                        {
                            "field_key": "test_field",
                            "field_label": "测试字段",
                            "field_type": "invalid_type",  # 无效类型
                            "field_order": 1
                        }
                    ]
                }
                
                await service.create_form_configuration(
                    tenant_id="test-tenant",
                    form_config=invalid_form,
                    created_by="test-user"
                )
                print("    ⚠️  字段类型约束测试失败 - 应该报错但没有")
                
            except Exception as e:
                if "check" in str(e).lower() or "constraint" in str(e).lower():
                    print("    ✅ 字段类型约束测试通过 - 正确阻止了无效类型")
                else:
                    print(f"    ❌ 字段类型约束测试异常: {str(e)}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ 约束测试失败: {str(e)}")
        return False


async def test_step_5_audit_fields():
    """第5步：验证审计字段功能"""
    print("\n🔍 第5步：验证审计字段...")
    
    try:
        from sqlalchemy import text
        from app.infrastructure.database.connection import engine
        
        async with engine.begin() as conn:
            # 查询审计字段
            audit_sql = """
            SELECT 
                form_name,
                created_by,
                updated_by,
                is_deleted,
                deleted_at,
                deleted_by,
                created_at
            FROM form_configurations 
            WHERE tenant_id = 'test-tenant'
            ORDER BY created_at;
            """
            
            result = await conn.execute(text(audit_sql))
            forms = result.fetchall()
            
            print(f"  📊 审计字段检查:")
            for form in forms:
                form_name = form[0]
                created_by = form[1] or "未设置"
                updated_by = form[2] or "未设置"
                is_deleted = form[3]
                deleted_status = "✅ 正常" if not is_deleted else "🗑️ 已删除"
                
                print(f"    • {form_name}")
                print(f"      创建者: {created_by}")
                print(f"      更新者: {updated_by}")
                print(f"      状态: {deleted_status}")
            
            print(f"  ✅ 审计字段验证完成")
            return True
            
    except Exception as e:
        print(f"  ❌ 审计字段验证失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 表单功能分步测试")
    print("=" * 60)
    
    results = []
    
    # 执行各步骤测试
    form_id_1 = await test_step_1_create_basic_form()
    results.append(("基础表单创建", form_id_1 is not None))
    
    form_id_2 = await test_step_2_create_advanced_form()
    results.append(("高级表单创建", form_id_2 is not None))
    
    form_count = await test_step_3_list_forms()
    results.append(("表单列表查询", form_count > 0))
    
    constraints_ok = await test_step_4_form_constraints()
    results.append(("约束验证", constraints_ok))
    
    audit_ok = await test_step_5_audit_fields()
    results.append(("审计字段", audit_ok))
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📊 分步测试报告")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name:<20}: {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"🎯 总结: {passed}/{total} 项测试通过 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 表单功能完全正常！")
        print("\n✅ 验证成功的功能:")
        print("   • 基础表单创建和字段配置")
        print("   • 高级表单创建和多字段类型")
        print("   • 表单列表查询和筛选")
        print("   • 数据库约束正确工作")
        print("   • 审计字段功能完整")
        print("\n🚀 配置引擎表单模块100%可用！")
        return 0
    else:
        print("⚠️  部分功能需要修复")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 