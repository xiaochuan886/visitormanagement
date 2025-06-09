from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 生成admin123的哈希
password = 'admin123'
hashed = pwd_context.hash(password)

print(f'原密码: {password}')
print(f'新哈希: {hashed}')
print(f'验证测试: {pwd_context.verify(password, hashed)}')

# 更新数据库
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
    cursor.execute(
        "UPDATE employees SET password_hash = %s WHERE email = %s",
        (hashed, 'admin@company.com')
    )
    conn.commit()
    
    print(f'密码哈希已更新到数据库')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'数据库更新失败: {e}') 