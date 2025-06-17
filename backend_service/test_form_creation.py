#!/usr/bin/env python3
"""
专门测试表单创建的脚本
"""
import asyncio
import json
from app.infrastructure.database.connection import get_db
from app.application.services.config_services_simple import SimpleFormConfigurationService


async def test_form_creation():
    """测试表单创建"""
    try:
        async for db in get_db():
            service = SimpleFormConfigurationService(db)
            
            # 准备测试数据
            form_config = {
                "form_name": "test_form_direct",
                "form_type": "visitor_registration",
                "description": "测试表单",
                "form_fields": [
                    {
                        "field_key": "visitor_name",
                        "field_label": "访客姓名",
                        "field_type": "text",
                        "field_order": 1,
                        "is_required": True
                    },
                    {
                        "field_key": "visitor_phone",
                        "field_label": "联系电话",
                        "field_type": "phone",
                        "field_order": 2,
                        "is_required": True
                    }
                ]
            }
            
            print("🧪 开始直接测试表单创建...")
            print(f"📝 测试数据: {json.dumps(form_config, indent=2, ensure_ascii=False)}")
            
            result = await service.create_form_configuration(
                tenant_id="test-tenant",
                form_config=form_config,
                created_by="test-user"
            )
            
            print(f"✅ 表单创建成功: {json.dumps(result, indent=2, ensure_ascii=False)}")
            break
            
    except Exception as e:
        print(f"❌ 表单创建失败: {str(e)}")
        import traceback
        print(f"详细错误信息:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_form_creation()) 