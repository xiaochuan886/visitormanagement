#!/usr/bin/env python3
"""
清理测试数据脚本
清理之前创建的测试表单，为新测试做准备
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database.connection import engine
from sqlalchemy import text


async def cleanup_test_forms():
    """清理测试表单数据"""
    print("🧹 开始清理测试表单数据...")
    
    try:
        async with engine.begin() as conn:
            # 查看现有测试数据
            check_sql = """
            SELECT id, form_name, form_type, tenant_id, created_at 
            FROM form_configurations 
            WHERE tenant_id = 'test-tenant' 
            ORDER BY created_at DESC;
            """
            
            result = await conn.execute(text(check_sql))
            forms = result.fetchall()
            
            print(f"📋 发现 {len(forms)} 个测试表单:")
            for form in forms:
                print(f"  - {form[1]} ({form[2]}) - {form[0]}")
            
            if forms:
                # 删除测试表单数据（先删除字段配置，再删除表单）
                print("🗑️  删除测试表单字段配置...")
                delete_fields_sql = """
                DELETE FROM form_field_configurations 
                WHERE form_config_id IN (
                    SELECT id FROM form_configurations 
                    WHERE tenant_id = 'test-tenant'
                );
                """
                await conn.execute(text(delete_fields_sql))
                
                print("🗑️  删除测试表单配置...")
                delete_forms_sql = """
                DELETE FROM form_configurations 
                WHERE tenant_id = 'test-tenant';
                """
                await conn.execute(text(delete_forms_sql))
                
                print(f"✅ 成功清理 {len(forms)} 个测试表单")
            else:
                print("✅ 没有发现需要清理的测试数据")
            
            return True
            
    except Exception as e:
        print(f"❌ 清理失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print("🧹 测试数据清理")
    print("=" * 50)
    
    success = await cleanup_test_forms()
    
    if success:
        print("\n🎉 测试数据清理完成！")
        print("📋 现在可以重新进行表单创建测试")
        return 0
    else:
        print("\n❌ 清理失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 