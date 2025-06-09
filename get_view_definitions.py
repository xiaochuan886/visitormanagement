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
    
    # 获取所有视图定义
    views = ['visitor_details', 'department_stats', 'employee_visitor_stats', 'visitor_status_stats']
    
    for view in views:
        cursor.execute(f"""
            SELECT pg_get_viewdef('{view}', true);
        """)
        result = cursor.fetchone()
        print(f'=== {view.upper()} ===')
        print(result[0])
        print('')
        
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'Error: {e}') 