import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DATABASE_HOST', 'localhost'),
        port=os.getenv('DATABASE_PORT', '5432'),
        database=os.getenv('DATABASE_NAME', 'visitor_management'),
        user=os.getenv('DATABASE_USER', 'postgres'),
        password=os.getenv('DATABASE_PASSWORD', '123456')
    )
    
    cursor = conn.cursor()
    
    # 检查管理员账户
    cursor.execute("""
        SELECT id, name, email, employee_id, status, password_hash, is_deleted
        FROM employees 
        WHERE email = %s
    """, ('admin@company.com',))
    
    result = cursor.fetchone()
    
    if result:
        print('管理员用户详情:')
        print(f'  ID: {result[0]}')
        print(f'  姓名: {result[1]}')
        print(f'  邮箱: {result[2]}')
        print(f'  员工号: {result[3]}')
        print(f'  状态: {result[4]}')
        print(f'  密码哈希: {result[5][:50] if result[5] else None}...')
        print(f'  是否删除: {result[6]}')
        
        # 检查角色分配
        cursor.execute("""
            SELECT r.name, r.permissions 
            FROM user_roles r
            JOIN employee_roles er ON r.id = er.role_id
            WHERE er.employee_id = %s
        """, (result[0],))
        
        roles = cursor.fetchall()
        print(f'\n角色分配:')
        for role in roles:
            print(f'  - {role[0]}: {role[1]}')
    else:
        print('没有找到管理员用户')
        
        # 查看所有用户
        cursor.execute("SELECT email, status FROM employees LIMIT 10")
        users = cursor.fetchall()
        print('\n现有用户:')
        for user in users:
            print(f'  - {user[0]} ({user[1]})')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}') 