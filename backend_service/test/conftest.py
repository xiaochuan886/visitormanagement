"""
pytest配置文件

提供测试环境配置、数据库初始化、测试夹具等。
"""

import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import Base
from app.infrastructure.database.session import get_session
from app.main import app


# 测试数据库配置
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/visitor_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    
    def override_get_session():
        return test_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_tenant_id() -> str:
    """测试租户ID"""
    return "test-tenant"


@pytest.fixture
def test_user_info() -> dict:
    """测试用户信息"""
    return {
        "user_id": "test-user-123",
        "email": "admin@test.com",
        "roles": ["admin"],
        "tenant_id": "test-tenant"
    }


@pytest.fixture
def auth_headers(test_user_info) -> dict:
    """认证头信息"""
    # 这里简化处理，实际应该生成真实的JWT token
    return {
        "Authorization": "Bearer test-token",
        "X-Tenant-ID": test_user_info["tenant_id"],
        "X-User-ID": test_user_info["user_id"]
    }


# pytest配置
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 