# 后端性能优化指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 后端开发者、性能工程师、运维工程师

## 🎯 性能目标

### 当前性能指标
- ✅ **API响应时间**: < 200ms (P95)
- ✅ **数据库查询**: < 50ms (平均)
- ✅ **并发用户**: 1000+ 同时在线
- ✅ **系统可用性**: 99.9%
- ✅ **内存使用**: < 2GB (典型负载)

### 优化目标
- 🎯 **API响应时间**: < 100ms (P95)
- 🎯 **查询性能**: < 30ms (平均)
- 🎯 **并发支持**: 2000+ 用户
- 🎯 **资源利用**: CPU < 70%, 内存 < 80%

## 🗄️ 数据库性能优化

### 索引优化策略

#### 1. 核心索引清单
```sql
-- 访客管理核心索引 (34个性能优化索引)

-- 1. 主要业务查询索引
CREATE INDEX idx_visitors_tenant_status ON visitors(tenant_id, status) WHERE is_deleted = false;
CREATE INDEX idx_visitors_expected_date ON visitors(expected_date) WHERE is_deleted = false;
CREATE INDEX idx_visitors_employee_id ON visitors(employee_id);
CREATE INDEX idx_visitors_phone_checkin ON visitors(phone_number, checkin_date);

-- 2. 复合索引优化
CREATE INDEX idx_visitors_composite_query ON visitors(tenant_id, status, expected_date, employee_id) 
WHERE is_deleted = false;

-- 3. 员工查询索引
CREATE INDEX idx_employees_tenant_department ON employees(tenant_id, department_id) WHERE is_deleted = false;
CREATE INDEX idx_employees_search ON employees(name, employee_id, email) WHERE is_deleted = false;

-- 4. 配置引擎索引
CREATE INDEX idx_form_configs_active ON form_configurations(tenant_id, is_active, form_type) 
WHERE is_deleted = false;
CREATE INDEX idx_workflow_configs_priority ON workflow_configurations(tenant_id, priority_level, is_active) 
WHERE is_deleted = false;

-- 5. 审计查询索引  
CREATE INDEX idx_audit_created_at ON visitors(created_at) WHERE is_deleted = false;
CREATE INDEX idx_audit_tenant_user ON visitors(tenant_id, created_by);
```

#### 2. 查询性能分析
```python
# tools/query_analyzer.py
import asyncio
from sqlalchemy import text, create_engine
import time

class QueryAnalyzer:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)

    async def analyze_slow_queries(self):
        """分析慢查询"""
        queries = [
            ("访客列表分页查询", """
                SELECT v.*, e.name as employee_name, d.name as department_name
                FROM visitors v
                LEFT JOIN employees e ON v.employee_id = e.id
                LEFT JOIN departments d ON e.department_id = d.id
                WHERE v.tenant_id = 'default_tenant'
                  AND v.is_deleted = false
                ORDER BY v.created_at DESC
                LIMIT 20 OFFSET 0
            """),
            ("访客状态统计查询", """
                SELECT status, COUNT(*) as count
                FROM visitors
                WHERE tenant_id = 'default_tenant'
                  AND is_deleted = false
                  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY status
            """),
            ("部门访客数量统计", """
                SELECT d.name, COUNT(v.id) as visitor_count
                FROM departments d
                LEFT JOIN employees e ON d.id = e.department_id
                LEFT JOIN visitors v ON e.id = v.employee_id
                WHERE d.tenant_id = 'default_tenant'
                  AND d.is_deleted = false
                  AND (v.is_deleted = false OR v.id IS NULL)
                GROUP BY d.id, d.name
                ORDER BY visitor_count DESC
            """)
        ]

        results = []
        with self.engine.connect() as conn:
            for name, query in queries:
                # 执行查询分析
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {query}"
                
                start_time = time.time()
                result = conn.execute(text(query))
                list(result)  # 消费结果
                execution_time = (time.time() - start_time) * 1000
                
                explain_result = conn.execute(text(explain_query))
                explain_plan = "\n".join([str(row[0]) for row in explain_result])
                
                results.append({
                    "query_name": name,
                    "execution_time_ms": execution_time,
                    "explain_plan": explain_plan
                })

        return results

    def suggest_optimizations(self, query_results: list):
        """建议查询优化"""
        suggestions = []
        
        for result in query_results:
            if result["execution_time_ms"] > 100:
                suggestions.append({
                    "query": result["query_name"],
                    "issue": "查询时间过长",
                    "suggestion": "考虑添加复合索引或优化查询逻辑"
                })
        
        return suggestions
```

### 连接池优化
```python
# app/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self, database_url: str):
        # 连接池配置优化
        self.engine = create_async_engine(
            database_url,
            # 连接池参数优化
            pool_size=20,           # 连接池大小
            max_overflow=30,        # 最大溢出连接
            pool_pre_ping=True,     # 连接检查
            pool_recycle=3600,      # 连接回收时间(1小时)
            
            # 查询超时配置
            connect_args={
                "command_timeout": 30,
                "server_settings": {
                    "application_name": "visitor_management",
                    "jit": "off"  # 禁用JIT以减少首次查询延迟
                }
            },
            
            # 日志配置
            echo=False,  # 生产环境关闭SQL日志
            future=True
        )
        
        self.session_factory = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
```

### 批量操作优化
```python
# services/batch_service.py
from typing import List
from sqlalchemy import insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

class BatchService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create_visitors(self, visitors_data: List[dict]) -> List[int]:
        """批量创建访客"""
        # 使用批量插入而不是逐个插入
        stmt = insert(VisitorModel).values(visitors_data)
        stmt = stmt.returning(VisitorModel.id)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        return [row[0] for row in result]

    async def bulk_update_status(self, visitor_ids: List[int], new_status: str):
        """批量更新访客状态"""
        stmt = update(VisitorModel).where(
            VisitorModel.id.in_(visitor_ids)
        ).values(
            status=new_status,
            updated_at=datetime.utcnow()
        )
        
        await self.session.execute(stmt)
        await self.session.commit()

    async def upsert_employees(self, employees_data: List[dict]):
        """批量更新或插入员工"""
        # PostgreSQL UPSERT操作
        stmt = pg_insert(EmployeeModel).values(employees_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['employee_id', 'tenant_id'],
            set_=dict(
                name=stmt.excluded.name,
                email=stmt.excluded.email,
                phone_number=stmt.excluded.phone_number,
                updated_at=stmt.excluded.updated_at
            )
        )
        
        await self.session.execute(stmt)
        await self.session.commit()
```

## 🚀 缓存策略优化

### Redis缓存架构
```python
# app/infrastructure/cache/redis_client.py
import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
from functools import wraps

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=50,  # 连接池大小
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = await self.redis_client.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值"""
        try:
            serialized_value = pickle.dumps(value)
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception:
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """批量删除匹配模式的缓存"""
        keys = await self.redis_client.keys(pattern)
        if keys:
            return await self.redis_client.delete(*keys)
        return 0

# 缓存装饰器
def cache_result(key_prefix: str, ttl: int = 3600):
    """结果缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### 多层缓存策略
```python
# services/cached_service.py
class CachedVisitorService:
    def __init__(self, visitor_service: VisitorService, cache_manager: CacheManager):
        self.visitor_service = visitor_service
        self.cache_manager = cache_manager

    @cache_result("visitor_list", ttl=300)  # 5分钟缓存
    async def get_visitors_cached(self, tenant_id: str, filters: dict) -> List[dict]:
        """缓存访客列表"""
        return await self.visitor_service.get_visitors(tenant_id, filters)

    @cache_result("visitor_stats", ttl=600)  # 10分钟缓存
    async def get_visitor_statistics(self, tenant_id: str) -> dict:
        """缓存访客统计数据"""
        return await self.visitor_service.get_statistics(tenant_id)

    async def invalidate_visitor_cache(self, tenant_id: str):
        """清理访客相关缓存"""
        patterns = [
            f"visitor_list:*{tenant_id}*",
            f"visitor_stats:*{tenant_id}*",
            f"department_stats:*{tenant_id}*"
        ]
        
        for pattern in patterns:
            await self.cache_manager.delete_pattern(pattern)

    async def create_visitor_with_cache(self, visitor_data: dict, created_by: str):
        """创建访客并清理相关缓存"""
        result = await self.visitor_service.create_visitor(visitor_data, created_by)
        
        # 清理相关缓存
        await self.invalidate_visitor_cache(visitor_data.get("tenant_id"))
        
        return result
```

## 🎮 应用层性能优化

### 异步处理优化
```python
# services/async_processing.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable

class AsyncProcessor:
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_batch_async(self, items: List[Any], processor: Callable) -> List[Any]:
        """并行处理批量任务"""
        tasks = [asyncio.create_task(processor(item)) for item in items]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def process_with_semaphore(self, items: List[Any], processor: Callable, max_concurrent: int = 5):
        """使用信号量控制并发数"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_processor(item):
            async with semaphore:
                return await processor(item)
        
        tasks = [asyncio.create_task(bounded_processor(item)) for item in items]
        return await asyncio.gather(*tasks)

# 使用示例
class VisitorProcessingService:
    def __init__(self, async_processor: AsyncProcessor):
        self.async_processor = async_processor

    async def process_visitor_notifications(self, visitors: List[VisitorModel]):
        """并行处理访客通知"""
        async def send_notification(visitor):
            try:
                await notification_service.send_visitor_notification(visitor)
                return {"visitor_id": visitor.id, "status": "success"}
            except Exception as e:
                return {"visitor_id": visitor.id, "status": "failed", "error": str(e)}

        results = await self.async_processor.process_with_semaphore(
            visitors, send_notification, max_concurrent=10
        )
        
        return results
```

### 内存优化
```python
# utils/memory_optimizer.py
import gc
import psutil
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def memory_monitor(func):
    """内存使用监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 记录开始内存
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = await func(*args, **kwargs)
            
            # 记录结束内存
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = end_memory - start_memory
            
            if memory_diff > 50:  # 如果内存增长超过50MB
                logger.warning(f"{func.__name__} 内存增长: {memory_diff:.2f}MB")
                gc.collect()  # 触发垃圾回收
            
            return result
        except Exception as e:
            logger.error(f"{func.__name__} 执行失败: {e}")
            raise
    
    return wrapper

class MemoryOptimizer:
    @staticmethod
    def optimize_large_query_result(query_result: List[dict]) -> List[dict]:
        """优化大查询结果的内存使用"""
        # 删除不必要的字段
        optimized_result = []
        for item in query_result:
            optimized_item = {k: v for k, v in item.items() if v is not None}
            optimized_result.append(optimized_item)
        
        return optimized_result

    @staticmethod
    async def stream_large_dataset(query_func, batch_size: int = 1000):
        """流式处理大数据集"""
        offset = 0
        while True:
            batch = await query_func(limit=batch_size, offset=offset)
            if not batch:
                break
            
            yield batch
            offset += batch_size
            
            # 主动触发垃圾回收
            if offset % 10000 == 0:
                gc.collect()
```

## 📊 性能监控

### 性能指标收集
```python
# monitoring/performance_monitor.py
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, List
from collections import defaultdict, deque

@dataclass
class PerformanceMetric:
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: float

class PerformanceMonitor:
    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.aggregated_stats: Dict[str, List[float]] = defaultdict(list)

    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """记录请求性能"""
        metric = PerformanceMetric(
            endpoint=endpoint,
            method=method,
            response_time=response_time,
            status_code=status_code,
            timestamp=time.time()
        )
        
        self.metrics.append(metric)
        self.aggregated_stats[f"{method}:{endpoint}"].append(response_time)

    def get_performance_stats(self, time_window: int = 3600) -> dict:
        """获取性能统计"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        stats = {}
        endpoint_metrics = defaultdict(list)
        
        for metric in recent_metrics:
            key = f"{metric.method}:{metric.endpoint}"
            endpoint_metrics[key].append(metric.response_time)
        
        for endpoint, response_times in endpoint_metrics.items():
            if response_times:
                stats[endpoint] = {
                    "count": len(response_times),
                    "avg_response_time": sum(response_times) / len(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "p95_response_time": self._percentile(response_times, 0.95),
                    "p99_response_time": self._percentile(response_times, 0.99)
                }
        
        return stats

    def _percentile(self, data: List[float], p: float) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[min(index, len(sorted_data) - 1)]

# FastAPI中间件集成
from fastapi import Request, Response

class PerformanceMiddleware:
    def __init__(self, app, monitor: PerformanceMonitor):
        self.app = app
        self.monitor = monitor

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_time = (time.time() - start_time) * 1000  # ms
                self.monitor.record_request(
                    endpoint=request.url.path,
                    method=request.method,
                    response_time=response_time,
                    status_code=message["status"]
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)
```

### 性能报告生成
```python
# monitoring/performance_reporter.py
class PerformanceReporter:
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor

    async def generate_performance_report(self) -> dict:
        """生成性能报告"""
        stats = self.monitor.get_performance_stats()
        
        # 识别慢请求
        slow_endpoints = []
        for endpoint, metrics in stats.items():
            if metrics["avg_response_time"] > 200:  # 平均响应时间超过200ms
                slow_endpoints.append({
                    "endpoint": endpoint,
                    "avg_response_time": metrics["avg_response_time"],
                    "p95_response_time": metrics["p95_response_time"],
                    "request_count": metrics["count"]
                })

        # 生成优化建议
        recommendations = self._generate_recommendations(slow_endpoints)

        return {
            "overall_stats": stats,
            "slow_endpoints": slow_endpoints,
            "recommendations": recommendations,
            "generated_at": time.time()
        }

    def _generate_recommendations(self, slow_endpoints: List[dict]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for endpoint_data in slow_endpoints:
            endpoint = endpoint_data["endpoint"]
            avg_time = endpoint_data["avg_response_time"]
            
            if "visitors" in endpoint and avg_time > 300:
                recommendations.append(f"考虑为 {endpoint} 添加缓存策略")
            
            if "search" in endpoint and avg_time > 200:
                recommendations.append(f"考虑为 {endpoint} 优化搜索索引")
            
            if endpoint_data["request_count"] > 1000 and avg_time > 100:
                recommendations.append(f"{endpoint} 请求量大且响应慢，考虑添加读取副本")

        return recommendations
```

## 🛠️ 部署优化

### 应用程序配置优化
```python
# config/production_config.py
class ProductionConfig:
    # 数据库配置
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 30
    DATABASE_POOL_TIMEOUT = 30
    
    # Redis配置
    REDIS_POOL_SIZE = 50
    REDIS_SOCKET_TIMEOUT = 5
    
    # 应用配置
    WORKER_PROCESSES = 4  # 根据CPU核心数调整
    WORKER_CONNECTIONS = 1000
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    # 缓存配置
    CACHE_DEFAULT_TTL = 3600
    CACHE_LONG_TTL = 86400  # 24小时
    
    # 日志配置
    LOG_LEVEL = "INFO"
    ACCESS_LOG = True
    
    # 安全配置
    TRUSTED_HOSTS = ["yourdomain.com", "*.yourdomain.com"]
```

### Nginx配置优化
```nginx
# nginx.conf
upstream visitor_management {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    # Gzip压缩
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;
    gzip_min_length 1000;

    # 静态文件缓存
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API代理
    location /api/ {
        proxy_pass http://visitor_management;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 连接池优化
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # 超时配置
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓存配置
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_key "$request_method$request_uri";
    }
}
```

---

## 📞 技术支持

### 性能优化支持
- **负责人**: 性能工程团队
- **监控工具**: Prometheus + Grafana
- **问题反馈**: 性能监控告警群

### 相关文档
- [后端系统架构概览](./Backend_System_Architecture.md)
- [数据库迁移指南](./Database_Migration_Guide.md)
- [后端开发者指南](./Backend_Developer_Guide.md)