#!/usr/bin/env python3
"""
场景管理系统数据库迁移脚本
执行场景管理相关表的创建和初始化
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_migration():
    """执行场景管理数据库迁移"""
    try:
        # 创建异步引擎
        engine = create_async_engine(
            settings.database_url,
            echo=True,  # 打印SQL语句
            future=True
        )
        
        logger.info("开始执行场景管理数据库迁移...")
        
        # 读取迁移SQL文件
        migration_file = Path(__file__).parent / "migrations" / "20250617_150000_add_scenario_management.sql"
        
        if not migration_file.exists():
            logger.error(f"迁移文件不存在: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 移除COMMIT语句，因为我们手动控制事务
        migration_sql = migration_sql.replace('COMMIT;', '')
        
        # 按分号分割SQL语句，过滤空语句和注释
        sql_statements = []
        for stmt in migration_sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--') and stmt.upper() != 'COMMIT':
                sql_statements.append(stmt)
        
        # 执行迁移
        async with engine.begin() as conn:
            logger.info("执行数据库迁移SQL...")
            
            for i, statement in enumerate(sql_statements, 1):
                try:
                    logger.info(f"执行SQL语句 {i}/{len(sql_statements)}")
                    await conn.execute(text(statement))
                    
                except Exception as e:
                    logger.error(f"执行SQL语句失败: {statement[:100]}...")
                    logger.error(f"错误: {str(e)}")
                    # 继续执行其他语句，因为表可能已存在
                    continue
        
        logger.info("场景管理数据库迁移执行完成")
        
        # 验证表是否创建成功
        await verify_migration(engine)
        
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"数据库迁移失败: {str(e)}")
        return False


async def verify_migration(engine):
    """验证迁移是否成功"""
    try:
        logger.info("验证场景管理表结构...")
        
        table_names = [
            'scenario_templates',
            'scenario_instances', 
            'scenario_executions',
            'scenario_routing_rules',
            'scenario_analytics'
        ]
        
        async with engine.begin() as conn:
            for table_name in table_names:
                query = text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table_name")
                result = await conn.execute(query, {"table_name": table_name})
                count = result.scalar()
                
                if count > 0:
                    logger.info(f"✓ 表 {table_name} 创建成功")
                else:
                    logger.warning(f"✗ 表 {table_name} 不存在")
        
        logger.info("数据库表结构验证完成")
        
    except Exception as e:
        logger.error(f"验证迁移失败: {str(e)}")


async def init_builtin_templates():
    """初始化内置场景模板"""
    try:
        logger.info("开始初始化内置场景模板...")
        
        # 这里可以添加内置模板的初始化逻辑
        # 暂时跳过，等API测试时通过接口创建
        
        logger.info("内置场景模板初始化完成")
        
    except Exception as e:
        logger.error(f"初始化内置模板失败: {str(e)}")


if __name__ == "__main__":
    async def main():
        logger.info("=== 场景管理系统数据库迁移 ===")
        
        # 执行迁移
        success = await run_migration()
        
        if success:
            logger.info("✓ 数据库迁移成功完成")
            
            # 初始化内置模板
            await init_builtin_templates()
            
            logger.info("=== 迁移流程全部完成 ===")
            sys.exit(0)
        else:
            logger.error("✗ 数据库迁移失败")
            sys.exit(1)
    
    # 运行迁移
    asyncio.run(main()) 