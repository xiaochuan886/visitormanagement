#!/usr/bin/env python3
"""
简化版配置引擎审计字段迁移脚本
直接添加必需的审计字段
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database.connection import engine
from sqlalchemy import text


async def add_audit_fields():
    """为配置引擎表添加审计字段"""
    print("🚀 开始为配置引擎表添加审计字段...")
    
    # 需要添加字段的表
    tables = [
        'form_configurations',
        'workflow_configurations', 
        'spatial_configurations',
        'business_rules'
    ]
    
    # 审计字段SQL
    audit_fields = [
        "ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE NOT NULL",
        "ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE",
        "ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(100)"
    ]
    
    try:
        async with engine.begin() as conn:
            print("🔌 连接数据库成功")
            
            for table in tables:
                print(f"\n📝 处理表: {table}")
                
                for field_sql in audit_fields:
                    try:
                        sql = f"ALTER TABLE {table} {field_sql};"
                        await conn.execute(text(sql))
                        field_name = field_sql.split()[5]  # 提取字段名
                        print(f"  ✅ 添加字段 {field_name} 成功")
                    except Exception as e:
                        if "already exists" in str(e):
                            print(f"  ⚠️  字段 {field_name} 已存在，跳过")
                        else:
                            print(f"  ❌ 添加字段失败: {str(e)}")
                            raise
            
            print(f"\n🎉 所有表的审计字段添加完成！")
            
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False
    
    return True


async def verify_fields():
    """验证字段添加结果"""
    print("\n🔍 验证审计字段...")
    
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
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text(check_sql))
            rows = result.fetchall()
            
            print("\n📊 审计字段检查结果:")
            print("=" * 80)
            print(f"{'表名':<25} {'is_deleted':<12} {'deleted_at':<12} {'deleted_by':<12} {'状态'}")
            print("=" * 80)
            
            all_complete = True
            for row in rows:
                table_name, has_is_deleted, has_deleted_at, has_deleted_by = row
                
                status = "✅ 完整" if all([has_is_deleted, has_deleted_at, has_deleted_by]) else "❌ 缺失"
                if not all([has_is_deleted, has_deleted_at, has_deleted_by]):
                    all_complete = False
                
                print(f"{table_name:<25} {has_is_deleted:<12} {has_deleted_at:<12} {has_deleted_by:<12} {status}")
            
            print("=" * 80)
            
            return all_complete
            
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("🏗️  配置引擎审计字段迁移 - 简化版")
    print("=" * 60)
    
    # 添加字段
    success = await add_audit_fields()
    if not success:
        print("❌ 字段添加失败，退出")
        return 1
    
    # 验证结果
    success = await verify_fields()
    if not success:
        print("⚠️  部分字段添加可能不完整")
        return 1
    
    print("\n🎉 配置引擎审计字段迁移完成！")
    print("📋 下一步：")
    print("   1. 重启FastAPI服务")
    print("   2. 测试配置引擎API")
    print("   3. 验证表单创建功能")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 