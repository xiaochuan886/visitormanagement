#!/usr/bin/env python3
"""
Redis缓存功能测试
"""
import asyncio
import sys
sys.path.append('.')

from app.infrastructure.cache.redis_client import get_redis
from app.core.serializers import serialize_for_cache, deserialize_from_cache
from app.application.dto.employee_dto import EmployeeResponseDTO
from datetime import datetime


async def test_redis_serialization():
    """测试Redis序列化功能"""
    try:
        print("🔍 测试Redis连接...")
        redis = await get_redis()
        
        # 测试基本连接
        await redis.ping()
        print("✅ Redis连接正常")
        
        # 创建测试数据（包含datetime对象）
        test_employee = EmployeeResponseDTO(
            id=999,
            name="测试员工",
            employee_id="TEST001",
            email="test@example.com",
            phone_number="13900139000",
            department_id=1,
            position="测试工程师",
            manager_id=None,
            hire_date=datetime.now().date(),
            birth_date=None,
            gender="male",
            address="测试地址",
            emergency_contact="紧急联系人",
            emergency_phone="13800138000",
            salary=10000.0,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tenant_id="default"
        )
        
        print("🔍 测试序列化...")
        
        # 测试序列化
        serialized_data = serialize_for_cache(test_employee)
        print("✅ 序列化成功")
        
        # 测试存储到Redis
        cache_key = "test:employee:999"
        await redis.set(cache_key, serialized_data, expire=60, serialize=False)
        print("✅ Redis存储成功")
        
        # 测试从Redis读取
        cached_data = await redis.get(cache_key, deserialize=False)
        if cached_data:
            print("✅ Redis读取成功")
            
            # 测试反序列化
            deserialized_employee = deserialize_from_cache(cached_data, EmployeeResponseDTO)
            print("✅ 反序列化成功")
            
            # 验证数据完整性
            if (deserialized_employee.name == test_employee.name and 
                deserialized_employee.employee_id == test_employee.employee_id):
                print("✅ 数据完整性验证通过")
            else:
                print("❌ 数据完整性验证失败")
        else:
            print("❌ Redis读取失败")
        
        # 清理测试数据
        await redis.delete(cache_key)
        print("✅ 测试数据清理完成")
        
        print("🎉 Redis缓存功能测试完成！")
        
    except Exception as e:
        print(f"❌ Redis缓存测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_redis_serialization()) 