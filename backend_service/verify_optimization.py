#!/usr/bin/env python3
"""
数据库优化验证脚本
"""
import asyncio
import asyncpg

async def check_optimization():
    """检查数据库优化结果"""
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5433/visitor_management')
        
        # 检查约束
        constraints = await conn.fetch('''
            SELECT conname, contype, conrelid::regclass as table_name 
            FROM pg_constraint 
            WHERE conname LIKE 'chk_%' 
            ORDER BY conname;
        ''')
        
        print('=== 检查约束 ===')
        for row in constraints:
            print(f'{row["conname"]} ({row["contype"]}) on {row["table_name"]}')
        
        # 检查索引
        indexes = await conn.fetch('''
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE indexname LIKE 'idx_%' 
            ORDER BY tablename, indexname;
        ''')
        
        print(f'\n=== 性能索引 ({len(indexes)}个) ===')
        current_table = None
        for row in indexes:
            if row["tablename"] != current_table:
                current_table = row["tablename"]
                print(f'\n{current_table}:')
            print(f'  - {row["indexname"]}')
        
        # 检查枚举类型
        enums = await conn.fetch('''
            SELECT typname, enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE typname IN ('visitor_status', 'approval_action')
            ORDER BY typname, enumsortorder;
        ''')
        
        print('\n=== 枚举类型 ===')
        current_type = None
        for row in enums:
            if row['typname'] != current_type:
                current_type = row['typname']
                print(f'\n{current_type}:')
            print(f'  - {row["enumlabel"]}')
        
        # 检查触发器
        triggers = await conn.fetch('''
            SELECT tgname, tgrelid::regclass as table_name
            FROM pg_trigger 
            WHERE tgname LIKE '%update%'
            ORDER BY table_name, tgname;
        ''')
        
        print(f'\n=== 触发器 ({len(triggers)}个) ===')
        for row in triggers:
            print(f'{row["tgname"]} on {row["table_name"]}')
        
        # 检查视图
        views = await conn.fetch('''
            SELECT viewname 
            FROM pg_views 
            WHERE viewname IN ('visitor_details', 'department_stats', 'employee_visitor_stats')
            ORDER BY viewname;
        ''')
        
        print(f'\n=== 优化视图 ({len(views)}个) ===')
        for row in views:
            print(f'  - {row["viewname"]}')
        
        await conn.close()
        
        print('\n✅ 数据库优化验证完成！')
        print(f'- 约束: {len(constraints)}个')
        print(f'- 索引: {len(indexes)}个')
        print(f'- 枚举: {len(set(row["typname"] for row in enums))}个')
        print(f'- 触发器: {len(triggers)}个')
        print(f'- 视图: {len(views)}个')
        
    except Exception as e:
        print(f'❌ 验证失败: {e}')

if __name__ == '__main__':
    asyncio.run(check_optimization())