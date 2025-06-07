#!/usr/bin/env python3
"""检查访客状态字段类型"""
import asyncio
import asyncpg

async def check_status_type():
    conn = await asyncpg.connect('postgresql://postgres:password@localhost:5433/visitor_management')
    
    # 检查访客状态字段类型
    result = await conn.fetch('''
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'visitors' AND column_name = 'status';
    ''')
    
    print('=== 访客状态字段类型 ===')
    for row in result:
        print(f'字段: {row["column_name"]}')
        print(f'数据类型: {row["data_type"]}')
        print(f'用户定义类型: {row["udt_name"]}')
    
    # 检查新增的状态统计视图
    views = await conn.fetch('''
        SELECT viewname 
        FROM pg_views 
        WHERE viewname = 'visitor_status_stats';
    ''')
    
    print(f'\n=== 新增状态统计视图 ===')
    for row in views:
        print(f'视图: {row["viewname"]}')
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check_status_type()) 