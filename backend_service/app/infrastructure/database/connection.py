"""
数据库连接管理
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator

from app.core.config import settings

# 创建异步数据库引擎 - 优化版本
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,  # 连接池大小
    max_overflow=30,  # 最大溢出连接数
    pool_timeout=30,  # 连接超时时间
    connect_args={
        "server_settings": {
            "application_name": "visitor_management_system",
            "jit": "off",  # 关闭JIT以提高连接速度
        }
    }
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 创建基础模型类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话 - 优化版本"""
    async with async_session_factory() as session:
        try:
            # 设置租户上下文（如果需要）
            tenant_id = getattr(settings, 'default_tenant_id', 'default')
            await session.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
            
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_with_tenant(tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
    """获取带租户上下文的数据库会话"""
    async with async_session_factory() as session:
        try:
            # 设置租户上下文
            await session.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
            
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from app.infrastructure.database import models  # noqa: F401
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """关闭数据库连接"""
    await engine.dispose() 