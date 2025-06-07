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
    
    # 获取当前数据库的实际DDL信息
    print('=== 当前数据库表结构 ===')
    cursor.execute("""
        SELECT table_name, column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name IN ('sites', 'departments', 'designations', 'employees', 'visitors')
        ORDER BY table_name, ordinal_position;
    """)
    
    current_table = None
    for row in cursor.fetchall():
        table_name, column_name, data_type, is_nullable, column_default = row
        if table_name != current_table:
            print(f'\n--- {table_name.upper()} ---')
            current_table = table_name
        print(f'{column_name}: {data_type} ({"NULL" if is_nullable == "YES" else "NOT NULL"})')
    
    print('\n=== 约束信息 ===')
    cursor.execute("""
        SELECT conname, contype, pg_get_constraintdef(oid) as definition
        FROM pg_constraint 
        WHERE connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        AND contype IN ('c', 'f', 'u')
        ORDER BY contype, conname;
    """)
    
    constraint_count = 0
    for row in cursor.fetchall():
        conname, contype, definition = row
        constraint_type = {'c': 'CHECK', 'f': 'FOREIGN KEY', 'u': 'UNIQUE'}[contype]
        print(f'{constraint_type}: {conname} - {definition}')
        constraint_count += 1
    
    print(f'\n总约束数量: {constraint_count}')
    
    print('\n=== 索引信息 ===')
    cursor.execute("""
        SELECT indexname, tablename, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        AND tablename IN ('sites', 'departments', 'designations', 'employees', 'visitors')
        ORDER BY tablename, indexname;
    """)
    
    index_count = 0
    for row in cursor.fetchall():
        indexname, tablename, indexdef = row
        print(f'{tablename}.{indexname}: {indexdef}')
        index_count += 1
    
    print(f'\n总索引数量: {index_count}')
    
    print('\n=== 枚举类型 ===')
    cursor.execute("""
        SELECT t.typname, e.enumlabel
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid
        ORDER BY t.typname, e.enumsortorder;
    """)
    
    current_enum = None
    enum_count = 0
    for row in cursor.fetchall():
        typname, enumlabel = row
        if typname != current_enum:
            print(f'\n{typname}:')
            current_enum = typname
            enum_count += 1
        print(f'  - {enumlabel}')
    
    print(f'\n总枚举类型数量: {enum_count}')
    
    print('\n=== 触发器信息 ===')
    cursor.execute("""
        SELECT trigger_name, event_object_table, action_statement
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        ORDER BY event_object_table, trigger_name;
    """)
    
    trigger_count = 0
    for row in cursor.fetchall():
        trigger_name, table_name, action_statement = row
        print(f'{table_name}.{trigger_name}: {action_statement}')
        trigger_count += 1
    
    print(f'\n总触发器数量: {trigger_count}')
    
    print('\n=== 视图信息 ===')
    cursor.execute("""
        SELECT table_name, view_definition
        FROM information_schema.views
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    view_count = 0
    for row in cursor.fetchall():
        view_name, view_definition = row
        print(f'{view_name}: {view_definition[:100]}...')
        view_count += 1
    
    print(f'\n总视图数量: {view_count}')
    
    cursor.close()
    conn.close()
    print('\n数据库连接成功，信息获取完成')
    
except Exception as e:
    print(f'数据库连接失败: {e}') 