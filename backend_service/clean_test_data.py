"""
清理测试数据脚本
"""
import asyncio
import asyncpg

async def clean_test_data():
    conn = await asyncpg.connect(
        host='localhost',
        port=5434,
        database='visitormanagement',
        user='postgres',
        password='postgres'
    )
    
    try:
        # 清理测试数据
        result1 = await conn.execute('DELETE FROM form_field_configurations WHERE form_config_id IN (SELECT id FROM form_configurations WHERE form_name LIKE $1)', '%API测试表单%')
        result2 = await conn.execute('DELETE FROM form_configurations WHERE form_name LIKE $1', '%API测试表单%')
        print(f'✅ 测试数据清理完成: 清理了 {result1.split()[-1]} 个字段, {result2.split()[-1]} 个表单')
    except Exception as e:
        print(f'❌ 清理数据时出错: {e}')
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(clean_test_data()) 