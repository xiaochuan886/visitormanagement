import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5433'),
            database=os.getenv('DATABASE_NAME', 'visitor_management'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', 'password')
        )
        
        cursor = conn.cursor()
        
        # 读取迁移脚本
        with open('migrations/add_employee_authentication.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("开始执行员工认证系统迁移...")
        
        # 执行迁移脚本
        cursor.execute(migration_sql)
        conn.commit()
        
        print("迁移执行完成！")
        
        # 验证迁移结果
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'password_hash'
        """)
        password_field = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_roles")
        role_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM employees 
            WHERE email = 'admin@company.com' AND password_hash IS NOT NULL
        """)
        admin_count = cursor.fetchone()[0]
        
        print(f"\n验证结果:")
        print(f"- password_hash字段添加: {'成功' if password_field > 0 else '失败'}")
        print(f"- 角色创建数量: {role_count}")
        print(f"- 管理员账户创建: {'成功' if admin_count > 0 else '失败'}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'迁移执行失败: {e}')

if __name__ == "__main__":
    run_migration() 