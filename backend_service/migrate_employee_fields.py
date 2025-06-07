#!/usr/bin/env python3
"""
员工表字段迁移脚本
"""
import asyncio
import sys
sys.path.append('.')

from app.infrastructure.database.connection import get_db
from sqlalchemy import text


async def migrate_employee_fields():
    """迁移员工表字段"""
    async for db in get_db():
        try:
            print("开始迁移员工表字段...")
            
            # 添加新字段的SQL列表
            migration_sqls = [
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50);",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS position VARCHAR(100);",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_id INTEGER;",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS hire_date TIMESTAMP WITH TIME ZONE;",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS birth_date TIMESTAMP WITH TIME ZONE;",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS address VARCHAR(200);",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(100);",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS emergency_phone VARCHAR(20);",
                "ALTER TABLE employees ADD COLUMN IF NOT EXISTS salary FLOAT;"
            ]
            
            # 逐个执行字段添加
            for sql in migration_sqls:
                await db.execute(text(sql))
            print("✅ 新字段添加完成")
            
            # 为现有员工设置默认的employee_id
            update_sql = """
            UPDATE employees 
            SET employee_id = 'EMP' || LPAD(id::text, 6, '0') 
            WHERE employee_id IS NULL OR employee_id = '';
            """
            
            result = await db.execute(text(update_sql))
            print(f"✅ 更新了 {result.rowcount} 个员工的工号")
            
            # 添加约束（先检查是否存在）
            try:
                # 检查唯一约束是否存在
                check_unique = """
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'employees_employee_id_unique' 
                AND table_name = 'employees';
                """
                result = await db.execute(text(check_unique))
                if not result.fetchone():
                    await db.execute(text("ALTER TABLE employees ADD CONSTRAINT employees_employee_id_unique UNIQUE (employee_id);"))
                    print("✅ 唯一约束添加完成")
                else:
                    print("✅ 唯一约束已存在")
                
                # 检查外键约束是否存在
                check_fk = """
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'employees_manager_id_fkey' 
                AND table_name = 'employees';
                """
                result = await db.execute(text(check_fk))
                if not result.fetchone():
                    await db.execute(text("ALTER TABLE employees ADD CONSTRAINT employees_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES employees (id);"))
                    print("✅ 外键约束添加完成")
                else:
                    print("✅ 外键约束已存在")
                    
            except Exception as e:
                print(f"⚠️ 约束添加警告: {e}")
                # 约束添加失败不影响主流程
            
            # 设置employee_id为非空
            not_null_sql = "ALTER TABLE employees ALTER COLUMN employee_id SET NOT NULL;"
            await db.execute(text(not_null_sql))
            print("✅ employee_id设置为非空")
            
            await db.commit()
            print("🎉 员工表字段迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            await db.rollback()
            raise
        break


if __name__ == "__main__":
    asyncio.run(migrate_employee_fields()) 