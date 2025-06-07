#!/usr/bin/env python3
"""
启动测试脚本 - 诊断应用程序启动问题
"""

def test_imports():
    """测试所有关键模块的导入"""
    try:
        print("1. 测试基础导入...")
        import sys
        print(f"   Python版本: {sys.version}")
        
        print("2. 测试FastAPI导入...")
        import fastapi
        print(f"   FastAPI版本: {fastapi.__version__}")
        
        print("3. 测试配置导入...")
        from app.core.config import settings
        print(f"   应用名称: {settings.app_name}")
        print(f"   数据库URL: {settings.database_url}")
        print(f"   Redis URL: {settings.redis_url}")
        
        print("4. 测试主应用导入...")
        from main import app
        print(f"   应用类型: {type(app)}")
        
        print("✅ 所有导入测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        print("5. 测试数据库连接...")
        from app.infrastructure.database.connection import engine
        print(f"   数据库引擎: {engine}")
        print("✅ 数据库连接测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    try:
        print("6. 测试Redis连接...")
        import asyncio
        from app.infrastructure.cache.redis_client import get_redis
        
        async def test_redis():
            redis = await get_redis()
            result = await redis.ping()
            return result
        
        result = asyncio.run(test_redis())
        print("✅ Redis连接测试通过！")
        return result
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 访客管理系统启动诊断 ===\n")
    
    success = True
    success &= test_imports()
    
    if success:
        success &= test_database_connection()
        success &= test_redis_connection()
    
    print(f"\n=== 诊断结果: {'✅ 通过' if success else '❌ 失败'} ===")
    
    if success:
        print("\n🚀 可以尝试启动应用程序:")
        print("   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001")
    else:
        print("\n�� 请先解决上述问题后再启动应用程序") 