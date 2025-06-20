import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5433'),
            database=os.getenv('DATABASE_NAME', 'visitor_management'),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', 'password')
        )
        
        # 读取迁移脚本
        with open('migrations/fix_employee_authentication.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("开始执行员工认证系统迁移...")
        
        # 执行迁移脚本
        await conn.execute(migration_sql)
        
        print("迁移执行完成！")
        
        # 验证迁移结果
        password_field = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'password_hash'
        """)
        
        role_count = await conn.fetchval("SELECT COUNT(*) FROM user_roles")
        
        admin_count = await conn.fetchval("""
            SELECT COUNT(*) FROM employees 
            WHERE email = 'admin@example.com' AND password_hash IS NOT NULL
        """)
        
        print(f"\n验证结果:")
        print(f"- password_hash字段添加: {'成功' if password_field > 0 else '失败'}")
        print(f"- 角色创建数量: {role_count}")
        print(f"- 管理员账户创建: {'成功' if admin_count > 0 else '失败'}")
        
        await conn.close()
        
    except Exception as e:
        print(f'迁移执行失败: {e}')

if __name__ == "__main__":
    asyncio.run(run_migration()) 