import os
import psycopg2
from urllib.parse import urlparse

# 从环境变量获取数据库连接信息，使用Docker配置
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5433/visitor_management')
parsed = urlparse(database_url)

try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )
    
    cursor = conn.cursor()
    
    # 获取所有表名
    print('=== 数据库中的所有表 ===')
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f'总表数量: {len(all_tables)}')
    for table in all_tables:
        print(f'- {table}')
    
    # 获取每个表的详细结构
    print('\n=== 详细表结构 ===')
    for table_name in all_tables:
        print(f'\n--- {table_name.upper()} ---')
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        for row in cursor.fetchall():
            column_name, data_type, is_nullable, column_default, max_length = row
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            length_info = f"({max_length})" if max_length else ""
            default_info = f" DEFAULT {column_default}" if column_default else ""
            print(f'  {column_name}: {data_type}{length_info} {nullable}{default_info}')
    
    # 获取外键关系
    print('\n=== 外键关系 ===')
    cursor.execute("""
        SELECT 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' 
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name;
    """)
    
    for row in cursor.fetchall():
        table_name, column_name, foreign_table, foreign_column = row
        print(f'{table_name}.{column_name} -> {foreign_table}.{foreign_column}')
    
    # 获取所有视图
    print('\n=== 数据库视图 ===')
    cursor.execute("""
        SELECT table_name, view_definition
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    views = cursor.fetchall()
    print(f'总视图数量: {len(views)}')
    for view_name, view_def in views:
        print(f'\n--- {view_name} ---')
        print(f'{view_def[:200]}...' if len(view_def) > 200 else view_def)
    
    # 获取所有函数
    print('\n=== 数据库函数 ===')
    cursor.execute("""
        SELECT routine_name, routine_type
        FROM information_schema.routines
        WHERE routine_schema = 'public'
        ORDER BY routine_name;
    """)
    
    functions = cursor.fetchall()
    print(f'总函数数量: {len(functions)}')
    for func_name, func_type in functions:
        print(f'- {func_name} ({func_type})')
    
    cursor.close()
    conn.close()
    print('\n数据库完整信息获取完成')
    
except Exception as e:
    print(f'数据库连接失败: {e}') 