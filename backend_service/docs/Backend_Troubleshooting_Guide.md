# 后端故障排除与调试指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: 后端开发者、运维工程师、技术支持

## 🚨 常见问题诊断

### 数据库连接问题

#### 问题现象
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

#### 排查步骤
```bash
# 1. 检查数据库服务状态
sudo systemctl status postgresql

# 2. 检查数据库端口
netstat -nlp | grep 5432

# 3. 测试数据库连接
psql postgresql://user:password@host:port/database

# 4. 检查连接池状态
python -c "
from app.infrastructure.database.connection import get_session
import asyncio
async def test():
    async for session in get_session():
        print('Database connection OK')
asyncio.run(test())
"
```

#### 解决方案
```python
# app/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine
import logging

logger = logging.getLogger(__name__)

def create_database_engine(database_url: str):
    """创建数据库引擎，带错误处理"""
    try:
        engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # 连接检查
            pool_recycle=3600,   # 连接回收
            echo=False
        )
        logger.info("数据库引擎创建成功")
        return engine
    except Exception as e:
        logger.error(f"数据库引擎创建失败: {e}")
        raise
```

### Redis缓存问题

#### 问题现象
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

#### 排查步骤
```bash
# 1. 检查Redis服务
sudo systemctl status redis

# 2. 检查Redis连接
redis-cli ping

# 3. 检查Redis配置
redis-cli info

# 4. 测试Python连接
python -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())
"
```

#### 解决方案
```python
# app/infrastructure/cache/redis_client.py
import redis.asyncio as redis
import logging

logger = logging.getLogger(__name__)

class ResilientRedisClient:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化Redis客户端，带重试机制"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            logger.info("Redis客户端初始化成功")
        except Exception as e:
            logger.error(f"Redis客户端初始化失败: {e}")
            self.client = None

    async def get(self, key: str, default=None):
        """安全获取缓存值"""
        try:
            if not self.client:
                return default
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis GET失败: {e}")
            return default

    async def set(self, key: str, value, ttl: int = 3600):
        """安全设置缓存值"""
        try:
            if not self.client:
                return False
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.warning(f"Redis SET失败: {e}")
            return False
```

### API响应超时

#### 问题现象
```
504 Gateway Timeout
ReadTimeout: HTTPSConnectionPool(host='api.example.com', port=443)
```

#### 排查步骤
```bash
# 1. 检查API日志
tail -f logs/app.log | grep ERROR

# 2. 检查系统资源
top
free -h
df -h

# 3. 检查网络连接
netstat -an | grep ESTABLISHED | wc -l

# 4. 检查慢查询
psql -d database -c "SELECT query, query_start, now() - query_start AS duration FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;"
```

#### 解决方案
```python
# app/api/middleware/timeout_middleware.py
import asyncio
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: int = 30):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            # 设置超时
            response = await asyncio.wait_for(
                call_next(request), 
                timeout=self.timeout
            )
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # 记录慢请求
            if process_time > 5.0:
                logger.warning(f"慢请求: {request.url.path} 耗时 {process_time:.2f}s")
            
            return response
            
        except asyncio.TimeoutError:
            process_time = time.time() - start_time
            logger.error(f"请求超时: {request.url.path} 耗时 {process_time:.2f}s")
            raise HTTPException(status_code=504, detail="请求超时")
```

## 🔍 日志分析

### 日志配置优化
```python
# app/core/logging.py
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # 添加额外字段
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "tenant_id"):
            log_entry["tenant_id"] = record.tenant_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """设置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    
    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=100*1024*1024,  # 100MB
        backupCount=10
    )
    file_handler.setFormatter(JSONFormatter())
    
    # 错误日志处理器 - 按时间轮转
    error_handler = TimedRotatingFileHandler(
        "logs/error.log",
        when="midnight",
        interval=1,
        backupCount=30
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger
```

### 日志分析工具
```python
# tools/log_analyzer.py
import json
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class LogAnalyzer:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path

    def analyze_errors(self, hours: int = 24):
        """分析错误日志"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(self.log_file_path, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    log_time = datetime.fromisoformat(log_entry["timestamp"])
                    
                    if (log_time > cutoff_time and 
                        log_entry["level"] in ["ERROR", "CRITICAL"]):
                        errors.append(log_entry)
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # 按错误类型分组
        error_types = Counter()
        error_modules = Counter()
        
        for error in errors:
            error_types[error.get("message", "未知错误")]
            error_modules[error.get("module", "未知模块")]
        
        return {
            "total_errors": len(errors),
            "error_types": dict(error_types.most_common(10)),
            "error_modules": dict(error_modules.most_common(10)),
            "recent_errors": errors[-10:]  # 最近10个错误
        }

    def analyze_performance(self, hours: int = 24):
        """分析性能日志"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        slow_requests = []
        
        # 查找慢请求日志
        slow_request_pattern = re.compile(r'慢请求: (.+) 耗时 ([\d.]+)s')
        
        with open(self.log_file_path, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    log_time = datetime.fromisoformat(log_entry["timestamp"])
                    
                    if log_time > cutoff_time:
                        match = slow_request_pattern.search(log_entry.get("message", ""))
                        if match:
                            slow_requests.append({
                                "endpoint": match.group(1),
                                "duration": float(match.group(2)),
                                "timestamp": log_entry["timestamp"]
                            })
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # 按端点分组
        endpoint_performance = defaultdict(list)
        for req in slow_requests:
            endpoint_performance[req["endpoint"]].append(req["duration"])
        
        # 计算统计信息
        performance_stats = {}
        for endpoint, durations in endpoint_performance.items():
            performance_stats[endpoint] = {
                "count": len(durations),
                "avg_duration": sum(durations) / len(durations),
                "max_duration": max(durations),
                "min_duration": min(durations)
            }
        
        return performance_stats
```

## 🛠️ 调试工具

### 调试装饰器
```python
# utils/debug_tools.py
import functools
import time
import logging
import traceback
from typing import Any, Callable

logger = logging.getLogger(__name__)

def debug_trace(func: Callable) -> Callable:
    """函数调用跟踪装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        
        # 记录函数调用
        logger.debug(f"调用函数: {func_name}")
        logger.debug(f"参数: args={args}, kwargs={kwargs}")
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(f"函数执行完成: {func_name}, 耗时: {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数执行失败: {func_name}, 耗时: {execution_time:.3f}s")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"堆栈跟踪: {traceback.format_exc()}")
            raise
    
    return wrapper

def measure_time(operation_name: str = None):
    """性能测量装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # 转换为毫秒
                
                logger.info(f"性能测量: {name} 耗时 {duration:.2f}ms")
                return result
                
            except Exception as e:
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000
                logger.error(f"性能测量: {name} 失败，耗时 {duration:.2f}ms, 错误: {e}")
                raise
        
        return wrapper
    return decorator
```

### 数据库调试工具
```python
# tools/db_debug.py
from sqlalchemy import text
from app.infrastructure.database.connection import get_session

class DatabaseDebugger:
    def __init__(self):
        self.session = None

    async def check_connections(self):
        """检查数据库连接"""
        async for session in get_session():
            try:
                result = await session.execute(text("SELECT 1"))
                print("✅ 数据库连接正常")
                
                # 检查活跃连接数
                result = await session.execute(text("""
                    SELECT count(*) as active_connections 
                    FROM pg_stat_activity 
                    WHERE state = 'active'
                """))
                active_connections = result.scalar()
                print(f"📊 活跃连接数: {active_connections}")
                
                return True
            except Exception as e:
                print(f"❌ 数据库连接失败: {e}")
                return False

    async def check_slow_queries(self):
        """检查慢查询"""
        async for session in get_session():
            result = await session.execute(text("""
                SELECT 
                    query,
                    query_start,
                    now() - query_start AS duration,
                    state
                FROM pg_stat_activity 
                WHERE state = 'active' 
                  AND now() - query_start > interval '5 seconds'
                ORDER BY duration DESC
            """))
            
            slow_queries = result.fetchall()
            if slow_queries:
                print("⚠️ 发现慢查询:")
                for query in slow_queries:
                    print(f"  - 耗时: {query.duration}")
                    print(f"    查询: {query.query[:100]}...")
            else:
                print("✅ 未发现慢查询")

    async def check_table_stats(self):
        """检查表统计信息"""
        async for session in get_session():
            result = await session.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum
                FROM pg_stat_user_tables 
                ORDER BY n_live_tup DESC
                LIMIT 10
            """))
            
            tables = result.fetchall()
            print("📊 表统计信息:")
            for table in tables:
                print(f"  - {table.tablename}: {table.row_count} 行")
                if table.dead_rows > table.row_count * 0.1:
                    print(f"    ⚠️ 死行过多: {table.dead_rows}")
```

## 📊 健康检查

### 系统健康检查
```python
# api/routes/health.py
from fastapi import APIRouter, HTTPException
import psutil
import asyncio
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """系统健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # 数据库检查
    try:
        db_status = await check_database()
        health_status["checks"]["database"] = db_status
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Redis检查
    try:
        redis_status = await check_redis()
        health_status["checks"]["redis"] = redis_status
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # 系统资源检查
    health_status["checks"]["system"] = check_system_resources()
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

async def check_database():
    """检查数据库连接"""
    async for session in get_session():
        await session.execute(text("SELECT 1"))
        return {"status": "healthy"}

async def check_redis():
    """检查Redis连接"""
    try:
        await cache_manager.redis_client.ping()
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}

def check_system_resources():
    """检查系统资源"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status = "healthy"
    warnings = []
    
    if cpu_percent > 80:
        status = "warning"
        warnings.append(f"CPU使用率过高: {cpu_percent}%")
    
    if memory.percent > 85:
        status = "warning"
        warnings.append(f"内存使用率过高: {memory.percent}%")
    
    if disk.percent > 90:
        status = "warning"
        warnings.append(f"磁盘使用率过高: {disk.percent}%")
    
    return {
        "status": status,
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "warnings": warnings
    }
```

---

## 📞 技术支持

### 故障处理支持
- **负责人**: 技术运维团队
- **紧急联系**: 24小时值班电话
- **问题升级**: 按严重程度分级处理

### 相关文档
- [后端系统架构概览](./Backend_System_Architecture.md)
- [后端性能优化指南](./Backend_Performance_Guide.md)
- [数据库迁移指南](./Database_Migration_Guide.md) 