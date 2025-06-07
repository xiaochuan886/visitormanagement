# 运维指南

## 概述

本文档提供访客管理系统的完整运维指南，包括部署、监控、维护、故障排除和性能优化等方面的详细说明。

## 系统监控

### 1. 应用监控

#### Prometheus + Grafana监控栈

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

volumes:
  prometheus_data:
  grafana_data:
```

#### Prometheus配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'visitor-management'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### 应用指标收集

```python
# app/infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_VISITORS = Gauge(
    'active_visitors_total',
    'Number of active visitors'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

REDIS_CONNECTIONS = Gauge(
    'redis_connections_active',
    'Number of active Redis connections'
)

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # 处理请求
            response = await self.app(scope, receive, send)
            
            # 记录指标
            duration = time.time() - start_time
            method = request.method
            endpoint = request.url.path
            status_code = getattr(response, 'status_code', 200)
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
        
        return await self.app(scope, receive, send)

@app.get("/metrics")
async def metrics():
    """Prometheus指标端点"""
    return Response(generate_latest(), media_type="text/plain")

# 业务指标更新
async def update_business_metrics():
    """更新业务指标"""
    # 更新活跃访客数
    active_count = await get_active_visitors_count()
    ACTIVE_VISITORS.set(active_count)
    
    # 更新数据库连接数
    db_connections = await get_database_connection_count()
    DATABASE_CONNECTIONS.set(db_connections)
```

### 2. 日志管理

#### ELK Stack配置

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    ports:
      - "5044:5044"
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.5.0
    user: root
    volumes:
      - ./logging/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - logstash

volumes:
  elasticsearch_data:
```

#### 结构化日志配置

```python
# app/core/logging.py
import structlog
import logging
from datetime import datetime
import json

def configure_logging():
    """配置结构化日志"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# 日志中间件
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = structlog.get_logger()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time.time()
            
            # 记录请求开始
            self.logger.info(
                "请求开始",
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host,
                user_agent=request.headers.get("user-agent"),
                request_id=str(uuid.uuid4())
            )
            
            try:
                response = await self.app(scope, receive, send)
                
                # 记录请求完成
                duration = time.time() - start_time
                self.logger.info(
                    "请求完成",
                    method=request.method,
                    url=str(request.url),
                    status_code=getattr(response, 'status_code', 200),
                    duration=duration
                )
                
                return response
                
            except Exception as e:
                # 记录请求异常
                duration = time.time() - start_time
                self.logger.error(
                    "请求异常",
                    method=request.method,
                    url=str(request.url),
                    error=str(e),
                    duration=duration,
                    exc_info=True
                )
                raise
        
        return await self.app(scope, receive, send)
```

### 3. 告警配置

#### Prometheus告警规则

```yaml
# monitoring/alert_rules.yml
groups:
  - name: visitor_management_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "高错误率告警"
          description: "5分钟内错误率超过10%"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "响应时间过长"
          description: "95%分位响应时间超过1秒"

      - alert: DatabaseConnectionHigh
        expr: database_connections_active > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "数据库连接数过高"
          description: "数据库连接数超过80"

      - alert: DiskSpaceHigh
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "磁盘空间不足"
          description: "磁盘可用空间少于10%"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务不可用"
          description: "{{ $labels.instance }} 服务已停止"
```

#### AlertManager配置

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@visitor.com'
  smtp_auth_username: 'alerts@visitor.com'
  smtp_auth_password: 'password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@visitor.com'
        subject: '访客管理系统告警: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          告警: {{ .Annotations.summary }}
          描述: {{ .Annotations.description }}
          时间: {{ .StartsAt }}
          {{ end }}
    
    webhook_configs:
      - url: 'http://webhook:5000/alert'
        send_resolved: true
```

## 性能优化

### 1. 数据库优化

#### 查询优化

```sql
-- 慢查询分析
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 20;

-- 索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- 表大小分析
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 连接池优化

```python
# app/infrastructure/database/connection.py
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine

def create_optimized_engine(database_url: str):
    """创建优化的数据库引擎"""
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=20,          # 连接池大小
        max_overflow=30,       # 最大溢出连接
        pool_pre_ping=True,    # 连接预检查
        pool_recycle=3600,     # 连接回收时间（1小时）
        echo=False,            # 生产环境关闭SQL日志
        connect_args={
            "options": "-c timezone=utc",
            "application_name": "visitor_management",
            "connect_timeout": 10,
        }
    )
```

### 2. 缓存策略

#### Redis缓存配置

```python
# app/infrastructure/cache/redis_cache.py
import redis
import json
import pickle
from typing import Any, Optional
from datetime import timedelta

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(
            redis_url,
            decode_responses=False,  # 支持二进制数据
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存"""
        try:
            data = pickle.dumps(value)
            self.redis.setex(key, ttl, data)
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
    
    async def delete(self, key: str):
        """删除缓存"""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")

# 缓存装饰器
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(ttl=1800, key_prefix="visitor")
async def get_visitor_by_id(visitor_id: str):
    # 数据库查询逻辑
    pass
```

### 3. 应用优化

#### 异步处理

```python
# app/infrastructure/tasks/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "visitor_management",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.infrastructure.tasks.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.infrastructure.tasks.tasks.send_notification': {'queue': 'notifications'},
        'app.infrastructure.tasks.tasks.generate_report': {'queue': 'reports'},
    }
)

# 异步任务
@celery_app.task
def send_notification(notification_data: dict):
    """发送通知任务"""
    # 发送邮件/短信逻辑
    pass

@celery_app.task
def generate_visitor_report(report_params: dict):
    """生成访客报表任务"""
    # 报表生成逻辑
    pass

# 在API中使用异步任务
@app.post("/api/v1/visitors/{visitor_id}/approve")
async def approve_visitor(visitor_id: str, approval_data: ApprovalRequest):
    # 审批逻辑
    visitor = await visitor_service.approve_visitor(visitor_id, approval_data)
    
    # 异步发送通知
    send_notification.delay({
        "type": "visitor_approved",
        "visitor_id": visitor_id,
        "recipient": visitor.email
    })
    
    return visitor
```

## 备份与恢复

### 1. 数据库备份

#### 自动备份脚本

```bash
#!/bin/bash
# backup_database.sh - 数据库备份脚本

set -e

# 配置
BACKUP_DIR="/backup/postgresql"
RETENTION_DAYS=30
DB_NAME="visitor_management"
DB_HOST="localhost"
DB_USER="postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
echo "开始备份数据库: $DB_NAME"
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom \
    --compress=9 \
    --verbose \
    --file=$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump

# 验证备份
if [ $? -eq 0 ]; then
    echo "备份成功: ${DB_NAME}_${TIMESTAMP}.dump"
    
    # 测试备份完整性
    pg_restore --list $BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump > /dev/null
    if [ $? -eq 0 ]; then
        echo "备份文件完整性验证通过"
    else
        echo "警告: 备份文件可能损坏"
        exit 1
    fi
else
    echo "备份失败"
    exit 1
fi

# 清理旧备份
echo "清理超过 $RETENTION_DAYS 天的备份文件"
find $BACKUP_DIR -name "${DB_NAME}_*.dump" -mtime +$RETENTION_DAYS -delete

# 上传到云存储（可选）
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "上传备份到S3"
    aws s3 cp $BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump \
        s3://$AWS_S3_BUCKET/database-backups/
fi

echo "备份任务完成"
```

#### 增量备份配置

```bash
#!/bin/bash
# setup_wal_archiving.sh - 设置WAL归档

# 修改postgresql.conf
cat >> /etc/postgresql/15/main/postgresql.conf << EOF
# WAL归档配置
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backup/wal_archive/%f && cp %p /backup/wal_archive/%f'
archive_timeout = 300  # 5分钟
max_wal_senders = 3
wal_keep_size = 1GB
EOF

# 创建归档目录
mkdir -p /backup/wal_archive
chown postgres:postgres /backup/wal_archive

# 重启PostgreSQL
systemctl restart postgresql

echo "WAL归档配置完成"
```

### 2. 应用备份

#### 配置文件备份

```bash
#!/bin/bash
# backup_configs.sh - 配置文件备份脚本

BACKUP_DIR="/backup/configs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONFIG_BACKUP="$BACKUP_DIR/configs_$TIMESTAMP.tar.gz"

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $CONFIG_BACKUP \
    /etc/nginx/ \
    /etc/ssl/ \
    /opt/visitor-management/.env \
    /opt/visitor-management/docker-compose.yml \
    /etc/systemd/system/visitor-management.service

echo "配置文件备份完成: $CONFIG_BACKUP"
```

### 3. 恢复流程

#### 数据库恢复脚本

```bash
#!/bin/bash
# restore_database.sh - 数据库恢复脚本

BACKUP_FILE=$1
DB_NAME="visitor_management"
DB_HOST="localhost"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <备份文件路径>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "警告: 此操作将覆盖现有数据库!"
read -p "确认继续? (y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo "操作已取消"
    exit 0
fi

# 停止应用服务
echo "停止应用服务..."
systemctl stop visitor-management

# 备份当前数据库
echo "备份当前数据库..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --format=custom \
    --file=/tmp/${DB_NAME}_before_restore_$(date +%Y%m%d_%H%M%S).dump

# 删除现有数据库
echo "删除现有数据库..."
dropdb -h $DB_HOST -U $DB_USER $DB_NAME

# 创建新数据库
echo "创建新数据库..."
createdb -h $DB_HOST -U $DB_USER $DB_NAME

# 恢复数据
echo "恢复数据..."
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME \
    --verbose \
    --clean \
    --if-exists \
    $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "数据库恢复成功"
    
    # 启动应用服务
    echo "启动应用服务..."
    systemctl start visitor-management
    
    # 验证服务状态
    sleep 10
    if systemctl is-active --quiet visitor-management; then
        echo "应用服务启动成功"
    else
        echo "警告: 应用服务启动失败，请检查日志"
    fi
else
    echo "数据库恢复失败"
    exit 1
fi
```

## 故障排除

### 1. 常见问题诊断

#### 服务健康检查脚本

```bash
#!/bin/bash
# health_check.sh - 系统健康检查脚本

echo "=== 访客管理系统健康检查 ==="

# 检查服务状态
echo "1. 检查服务状态..."
services=("visitor-management" "postgresql" "redis" "nginx")
for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service: 运行中"
    else
        echo "✗ $service: 已停止"
    fi
done

# 检查端口监听
echo -e "\n2. 检查端口监听..."
ports=("8000:应用服务" "5432:PostgreSQL" "6379:Redis" "80:Nginx" "443:Nginx SSL")
for port_info in "${ports[@]}"; do
    port=$(echo $port_info | cut -d: -f1)
    name=$(echo $port_info | cut -d: -f2)
    if netstat -tuln | grep -q ":$port "; then
        echo "✓ $name (端口 $port): 监听中"
    else
        echo "✗ $name (端口 $port): 未监听"
    fi
done

# 检查数据库连接
echo -e "\n3. 检查数据库连接..."
if pg_isready -h localhost -p 5432 -U postgres; then
    echo "✓ PostgreSQL: 连接正常"
else
    echo "✗ PostgreSQL: 连接失败"
fi

# 检查Redis连接
echo -e "\n4. 检查Redis连接..."
if redis-cli ping | grep -q PONG; then
    echo "✓ Redis: 连接正常"
else
    echo "✗ Redis: 连接失败"
fi

# 检查API响应
echo -e "\n5. 检查API响应..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q 200; then
    echo "✓ API: 响应正常"
else
    echo "✗ API: 响应异常"
fi

# 检查磁盘空间
echo -e "\n6. 检查磁盘空间..."
df -h | awk 'NR>1 {
    if ($5+0 > 80) 
        print "⚠ " $6 ": " $5 " 使用率过高"
    else 
        print "✓ " $6 ": " $5 " 使用率正常"
}'

# 检查内存使用
echo -e "\n7. 检查内存使用..."
memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$memory_usage > 80" | bc -l) )); then
    echo "⚠ 内存使用率: ${memory_usage}% (过高)"
else
    echo "✓ 内存使用率: ${memory_usage}% (正常)"
fi

# 检查CPU负载
echo -e "\n8. 检查CPU负载..."
load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
cpu_cores=$(nproc)
if (( $(echo "$load_avg > $cpu_cores" | bc -l) )); then
    echo "⚠ CPU负载: $load_avg (过高，CPU核心数: $cpu_cores)"
else
    echo "✓ CPU负载: $load_avg (正常，CPU核心数: $cpu_cores)"
fi

echo -e "\n=== 健康检查完成 ==="
```

### 2. 日志分析

#### 日志分析脚本

```bash
#!/bin/bash
# analyze_logs.sh - 日志分析脚本

LOG_FILE="/var/log/visitor-management/app.log"
ERROR_LOG="/var/log/visitor-management/error.log"
NGINX_LOG="/var/log/nginx/access.log"

echo "=== 访客管理系统日志分析 ==="

# 分析错误日志
echo "1. 最近1小时的错误统计:"
if [ -f "$ERROR_LOG" ]; then
    grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" $ERROR_LOG | \
    awk '{print $4}' | sort | uniq -c | sort -nr
else
    echo "错误日志文件不存在"
fi

# 分析API访问
echo -e "\n2. 最近1小时的API访问统计:"
if [ -f "$NGINX_LOG" ]; then
    grep "$(date -d '1 hour ago' '+%d/%b/%Y:%H')" $NGINX_LOG | \
    awk '{print $7}' | grep "^/api" | sort | uniq -c | sort -nr | head -10
else
    echo "Nginx访问日志文件不存在"
fi

# 分析响应时间
echo -e "\n3. 慢请求分析 (>1秒):"
if [ -f "$LOG_FILE" ]; then
    grep "duration" $LOG_FILE | \
    awk '$NF > 1 {print $0}' | tail -10
else
    echo "应用日志文件不存在"
fi

# 分析数据库连接
echo -e "\n4. 数据库连接错误:"
if [ -f "$ERROR_LOG" ]; then
    grep -i "database\|connection" $ERROR_LOG | tail -5
else
    echo "无数据库连接错误"
fi
```

### 3. 性能问题排查

#### 性能诊断脚本

```python
# scripts/performance_diagnosis.py
import asyncio
import aiohttp
import time
import statistics
from typing import List

class PerformanceDiagnostic:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = {}
    
    async def test_endpoint(self, endpoint: str, concurrent: int = 10, requests: int = 100):
        """测试端点性能"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(requests):
                task = self.make_request(session, endpoint)
                tasks.append(task)
                
                # 控制并发数
                if len(tasks) >= concurrent:
                    results = await asyncio.gather(*tasks)
                    self.process_results(endpoint, results)
                    tasks = []
            
            # 处理剩余请求
            if tasks:
                results = await asyncio.gather(*tasks)
                self.process_results(endpoint, results)
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str):
        """发送请求并测量响应时间"""
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.text()
                duration = time.time() - start_time
                return {
                    'status': response.status,
                    'duration': duration,
                    'success': True
                }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'status': 0,
                'duration': duration,
                'success': False,
                'error': str(e)
            }
    
    def process_results(self, endpoint: str, results: List[dict]):
        """处理测试结果"""
        if endpoint not in self.results:
            self.results[endpoint] = []
        
        self.results[endpoint].extend(results)
    
    def generate_report(self):
        """生成性能报告"""
        report = {}
        
        for endpoint, results in self.results.items():
            durations = [r['duration'] for r in results if r['success']]
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            if durations:
                report[endpoint] = {
                    'total_requests': total_count,
                    'successful_requests': success_count,
                    'success_rate': success_count / total_count * 100,
                    'avg_response_time': statistics.mean(durations),
                    'min_response_time': min(durations),
                    'max_response_time': max(durations),
                    'p95_response_time': statistics.quantiles(durations, n=20)[18],  # 95th percentile
                    'p99_response_time': statistics.quantiles(durations, n=100)[98]  # 99th percentile
                }
        
        return report

async def main():
    diagnostic = PerformanceDiagnostic("http://localhost:8000")
    
    # 测试关键端点
    endpoints = [
        "/health",
        "/api/v1/visitors",
        "/api/v1/employees",
        "/api/v1/departments"
    ]
    
    for endpoint in endpoints:
        print(f"测试端点: {endpoint}")
        await diagnostic.test_endpoint(endpoint, concurrent=5, requests=50)
    
    # 生成报告
    report = diagnostic.generate_report()
    
    print("\n=== 性能测试报告 ===")
    for endpoint, metrics in report.items():
        print(f"\n端点: {endpoint}")
        print(f"  总请求数: {metrics['total_requests']}")
        print(f"  成功率: {metrics['success_rate']:.2f}%")
        print(f"  平均响应时间: {metrics['avg_response_time']:.3f}s")
        print(f"  95%分位响应时间: {metrics['p95_response_time']:.3f}s")
        print(f"  99%分位响应时间: {metrics['p99_response_time']:.3f}s")

if __name__ == "__main__":
    asyncio.run(main())
```

## 维护任务

### 1. 定期维护

#### 系统维护脚本

```bash
#!/bin/bash
# maintenance.sh - 系统维护脚本

echo "=== 开始系统维护 ==="

# 1. 清理日志文件
echo "1. 清理日志文件..."
find /var/log/visitor-management/ -name "*.log" -mtime +30 -delete
find /var/log/nginx/ -name "*.log" -mtime +30 -delete

# 2. 清理临时文件
echo "2. 清理临时文件..."
find /tmp -name "visitor_*" -mtime +1 -delete
find /opt/visitor-management/uploads/temp -mtime +1 -delete

# 3. 数据库维护
echo "3. 数据库维护..."
psql -h localhost -U postgres -d visitor_management -c "VACUUM ANALYZE;"
psql -h localhost -U postgres -d visitor_management -c "REINDEX DATABASE visitor_management;"

# 4. 清理过期数据
echo "4. 清理过期数据..."
python3 /opt/visitor-management/scripts/cleanup_expired_data.py

# 5. 更新统计信息
echo "5. 更新统计信息..."
psql -h localhost -U postgres -d visitor_management -c "ANALYZE;"

# 6. 检查磁盘空间
echo "6. 检查磁盘空间..."
df -h | awk '$5 > 80 {print "警告: " $6 " 磁盘使用率过高: " $5}'

# 7. 重启服务（如需要）
if [ "$1" = "--restart" ]; then
    echo "7. 重启服务..."
    systemctl restart visitor-management
    systemctl restart nginx
fi

echo "=== 系统维护完成 ==="
```

### 2. 数据清理

```python
# scripts/cleanup_expired_data.py
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.database.models import VisitorModel, AuditLogModel

class DataCleanup:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def cleanup_expired_visitors(self, days: int = 365):
        """清理过期访客记录"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 查找过期的已签出访客
        expired_visitors = await self.db.execute(
            select(VisitorModel)
            .where(VisitorModel.checkout_date < cutoff_date)
            .where(VisitorModel.status == 'checked_out')
        )
        
        count = 0
        for visitor in expired_visitors.scalars():
            # 匿名化敏感信息而不是删除
            visitor.name = f"访客_{visitor.id}"
            visitor.phone_number = "***"
            visitor.email = "***"
            visitor.identification_no = "***"
            count += 1
        
        await self.db.commit()
        print(f"匿名化了 {count} 条过期访客记录")
    
    async def cleanup_old_audit_logs(self, days: int = 2555):  # 7年
        """清理旧审计日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            delete(AuditLogModel)
            .where(AuditLogModel.created_at < cutoff_date)
        )
        
        await self.db.commit()
        print(f"删除了 {result.rowcount} 条旧审计日志")

async def main():
    async with get_async_session() as db:
        cleanup = DataCleanup(db)
        await cleanup.cleanup_expired_visitors()
        await cleanup.cleanup_old_audit_logs()

if __name__ == "__main__":
    asyncio.run(main())
```

---

本运维指南提供了完整的系统监控、性能优化、备份恢复和故障排除方案，确保访客管理系统的稳定运行和高可用性。 