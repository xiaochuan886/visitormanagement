#!/usr/bin/env python3
"""调试访客创建问题"""
import asyncio
import asyncpg
from datetime import datetime, timedelta
from app.infrastructure.database.models import VisitorModel
from app.infrastructure.database.connection import get_db
from app.application.services.visitor_service import VisitorService
from app.application.dto.visitor_dto import VisitorCreateDTO

async def debug_visitor_creation():
    """调试访客创建"""
    print("🔍 调试访客创建问题...")
    
    # 测试数据库连接
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5433/visitor_management')
        print("✅ 数据库连接成功")
        
        # 检查访客表结构
        result = await conn.fetch('''
            SELECT column_name, data_type, udt_name, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'visitors' 
            ORDER BY ordinal_position;
        ''')
        
        print("\n📋 访客表结构:")
        for row in result:
            print(f"  {row['column_name']}: {row['data_type']} ({row['udt_name']}) - 可空: {row['is_nullable']} - 默认值: {row['column_default']}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    # 测试访客服务
    try:
        async for db in get_db():
            visitor_service = VisitorService(db)
            
            # 创建测试访客数据
            visitor_data = VisitorCreateDTO(
                name="调试测试访客",
                phone_number="13900139000",
                email="debug@example.com",
                company_name="调试公司",
                purpose="business",
                expected_date=datetime.now() + timedelta(days=1),
                gender="male"
            )
            
            print(f"\n📝 创建访客数据: {visitor_data.dict()}")
            
            # 尝试创建访客
            result = await visitor_service.create_visitor(
                visitor_data=visitor_data,
                created_by="debug_user",
                tenant_id="default"
            )
            
            print(f"✅ 访客创建成功: ID={result.id}, 状态={result.status}")
            
    except Exception as e:
        print(f"❌ 访客创建失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(debug_visitor_creation()) 