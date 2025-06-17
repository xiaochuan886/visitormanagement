#!/usr/bin/env python3
"""
配置引擎审计字段迁移执行脚本
执行数据库迁移，为配置引擎表添加缺失的审计字段
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database.connection import engine
from sqlalchemy import text


async def execute_migration():
    """执行配置引擎审计字段迁移"""
    print("🚀 开始执行配置引擎审计字段迁移...")
    
    # 读取迁移脚本
    migration_file = Path(__file__).parent / "migrations" / "20250617_143000_add_config_audit_fields.sql"
    
    if not migration_file.exists():
        print(f"❌ 迁移文件不存在: {migration_file}")
        return False
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"📄 读取迁移脚本: {migration_file.name}")
    
    # 使用数据库引擎
    
    try:
        async with engine.begin() as conn:
            print("🔌 连接数据库成功，开始执行迁移...")
            
            # 分割SQL语句（按照分号分割，但忽略函数体内的分号）
            sql_statements = []
            current_statement = ""
            in_function = False
            paren_count = 0
            
            for line in migration_sql.split('\n'):
                line = line.strip()
                if not line or line.startswith('--'):
                    continue
                
                current_statement += line + "\n"
                
                # 检测函数定义开始
                if 'FUNCTION' in line.upper() or '$$' in line:
                    in_function = True
                
                # 检测函数定义结束
                if in_function and line.endswith('$$;'):
                    in_function = False
                    sql_statements.append(current_statement.strip())
                    current_statement = ""
                    continue
                
                # 检测DO块
                if line.upper().startswith('DO $$'):
                    paren_count = 1
                elif line.upper() == 'END $$;':
                    paren_count = 0
                    sql_statements.append(current_statement.strip())
                    current_statement = ""
                    continue
                elif 'BEGIN' in line.upper() and paren_count > 0:
                    paren_count += 1
                elif 'END' in line.upper() and paren_count > 0:
                    paren_count -= 1
                
                # 普通语句结束
                if not in_function and paren_count == 0 and line.endswith(';'):
                    sql_statements.append(current_statement.strip())
                    current_statement = ""
            
            # 执行SQL语句
            executed_count = 0
            for i, sql_stmt in enumerate(sql_statements):
                if sql_stmt.strip():
                    try:
                        await conn.execute(text(sql_stmt))
                        executed_count += 1
                        print(f"✅ 执行语句 {executed_count}: 成功")
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            print(f"⚠️  语句 {i+1}: 已存在，跳过")
                        else:
                            print(f"❌ 语句 {i+1} 执行失败: {str(e)}")
                            print(f"SQL: {sql_stmt[:100]}...")
                            raise
            
            print(f"🎉 迁移执行完成！共执行 {executed_count} 条语句")
            
    except Exception as e:
        print(f"❌ 迁移执行失败: {str(e)}")
        return False
    finally:
        await engine.dispose()
    
    return True


async def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    # 使用数据库引擎
    
    try:
        async with engine.begin() as conn:
            # 检查配置引擎表的审计字段
            check_sql = """
            SELECT 
                t.table_name,
                COUNT(CASE WHEN c.column_name = 'is_deleted' THEN 1 END) as has_is_deleted,
                COUNT(CASE WHEN c.column_name = 'deleted_at' THEN 1 END) as has_deleted_at,
                COUNT(CASE WHEN c.column_name = 'deleted_by' THEN 1 END) as has_deleted_by
            FROM information_schema.tables t
            LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
            WHERE t.table_name IN (
                'form_configurations', 'workflow_configurations', 
                'spatial_configurations', 'business_rules'
            )
            AND t.table_schema = 'public'
            GROUP BY t.table_name
            ORDER BY t.table_name;
            """
            
            result = await conn.execute(text(check_sql))
            rows = result.fetchall()
            
            print("\n📊 配置引擎表审计字段检查结果:")
            print("=" * 80)
            print(f"{'表名':<25} {'is_deleted':<12} {'deleted_at':<12} {'deleted_by':<12} {'状态'}")
            print("=" * 80)
            
            all_complete = True
            for row in rows:
                table_name = row[0]
                has_is_deleted = row[1]
                has_deleted_at = row[2] 
                has_deleted_by = row[3]
                
                status = "✅ 完整" if all([has_is_deleted, has_deleted_at, has_deleted_by]) else "❌ 缺失"
                if not all([has_is_deleted, has_deleted_at, has_deleted_by]):
                    all_complete = False
                
                print(f"{table_name:<25} {has_is_deleted:<12} {has_deleted_at:<12} {has_deleted_by:<12} {status}")
            
            print("=" * 80)
            
            if all_complete:
                print("🎉 所有配置引擎表的审计字段都已正确添加！")
            else:
                print("⚠️  部分表的审计字段还未完全添加")
                return False
            
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False
    finally:
        await engine.dispose()
    
    return True


async def main():
    """主函数"""
    print("=" * 60)
    print("🏗️  访客管理系统 - 配置引擎审计字段迁移")
    print("=" * 60)
    
    # 执行迁移
    success = await execute_migration()
    if not success:
        print("❌ 迁移失败，退出")
        return 1
    
    # 验证迁移结果
    success = await verify_migration()
    if not success:
        print("❌ 验证失败，请检查数据库状态")
        return 1
    
    print("\n🎉 配置引擎审计字段迁移完成！")
    print("📋 下一步建议：")
    print("   1. 重启FastAPI服务以应用新的数据库结构")
    print("   2. 运行API测试验证配置引擎功能")
    print("   3. 检查所有配置引擎API端点是否正常工作")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 