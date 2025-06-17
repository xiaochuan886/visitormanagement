#!/usr/bin/env python3
"""
检查配置引擎表结构
"""
import asyncio
from sqlalchemy import text
from app.infrastructure.database.connection import get_db


async def check_table_structure():
    """检查配置引擎表结构"""
    try:
        # 使用数据库连接检查表结构
        async for db in get_db():
            # 检查form_configurations表结构
            result = await db.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'form_configurations'
                ORDER BY ordinal_position;
            """))
            
            print("form_configurations 表结构:")
            print("列名".ljust(25), "数据类型".ljust(20), "可为空")
            print("-" * 60)
            
            for row in result.fetchall():
                print(f"{row[0]:<25} {row[1]:<20} {row[2]}")
            
            print("\n" + "="*60)
            
            # 检查是否存在is_deleted列
            result = await db.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'form_configurations' 
                AND column_name = 'is_deleted';
            """))
            
            count = result.scalar()
            if count > 0:
                print("✅ form_configurations表包含is_deleted列")
            else:
                print("❌ form_configurations表缺少is_deleted列")
                
            # 同样检查其他配置表
            tables = ['workflow_configurations', 'spatial_configurations', 'business_rules']
            
            for table in tables:
                result = await db.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    AND column_name = 'is_deleted';
                """))
                
                count = result.scalar()
                if count > 0:
                    print(f"✅ {table}表包含is_deleted列")
                else:
                    print(f"❌ {table}表缺少is_deleted列")
            break

    except Exception as e:
        print(f"检查表结构失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(check_table_structure()) 