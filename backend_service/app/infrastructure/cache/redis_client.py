"""
Redis缓存客户端
"""
import json
import pickle
from typing import Any, Optional, Union
import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings


class RedisClient:
    """Redis异步客户端"""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
    
    async def connect(self) -> None:
        """连接Redis"""
        self._redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
    
    async def ping(self) -> bool:
        """检查Redis连接"""
        if not self._redis:
            return False
        try:
            return await self._redis.ping()
        except Exception:
            return False
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """设置缓存值"""
        if not self._redis:
            await self.connect()
        
        try:
            if serialize:
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self._redis.set(key, value, ex=expire)
            return result is True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def get(
        self, 
        key: str, 
        deserialize: bool = True
    ) -> Optional[Any]:
        """获取缓存值"""
        if not self._redis:
            await self.connect()
        
        try:
            value = await self._redis.get(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self._redis:
            await self.connect()
        
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            await self.connect()
        
        try:
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        if not self._redis:
            await self.connect()
        
        try:
            result = await self._redis.expire(key, seconds)
            return result is True
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        if not self._redis:
            await self.connect()
        
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            print(f"Redis ttl error: {e}")
            return -1
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配模式的所有键"""
        if not self._redis:
            await self.connect()
        
        try:
            return await self._redis.keys(pattern)
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not self._redis:
            await self.connect()
        
        try:
            result = await self._redis.flushdb()
            return result is True
        except Exception as e:
            print(f"Redis flushdb error: {e}")
            return False
    
    async def publish(self, channel: str, message: Any) -> int:
        """发布消息到频道"""
        if not self._redis:
            await self.connect()
        
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, ensure_ascii=False)
            return await self._redis.publish(channel, message)
        except Exception as e:
            print(f"Redis publish error: {e}")
            return 0
    
    async def subscribe(self, *channels):
        """订阅频道"""
        if not self._redis:
            await self.connect()
        
        try:
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            print(f"Redis subscribe error: {e}")
            return None


# 全局Redis客户端实例
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """获取Redis客户端实例"""
    if not await redis_client.ping():
        await redis_client.connect()
    return redis_client 