#!/usr/bin/env python3
"""
表单创建调试脚本
专门用于调试表单创建过程中的具体错误
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database.connection import async_session_factory
from app.application.services.config_services_simple import SimpleFormConfigurationService


async def test_form_creation():
    """测试表单创建功能"""
    print("🧪 开始调试表单创建...")
    
    # 简化的表单数据
    form_data = {
        "form_name": "访客登记表单",
        "form_type": "visitor_registration",
        "description": "访客登记表单测试",
        "form_fields": [
            {
                "field_key": "visitor_name",
                "field_label": "访客姓名",
                "field_type": "text",
                "field_order": 1,
                "is_required": True
            }
        ]
    }
    
    try:
        async with async_session_factory() as session:
            service = SimpleFormConfigurationService(session)
            
            print("📋 创建表单配置...")
            print(f"表单数据: {form_data}")
            
            result = await service.create_form_configuration(
                tenant_id="test-tenant",
                form_config=form_data,
                created_by="test-user"
            )
            
            print(f"✅ 表单创建成功: {result}")
            return True
            
    except Exception as e:
        print(f"❌ 表单创建失败: {str(e)}")
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("🐛 表单创建调试")
    print("=" * 60)
    
    success = await test_form_creation()
    
    if success:
        print("\n🎉 表单创建调试成功！")
        return 0
    else:
        print("\n❌ 表单创建调试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 