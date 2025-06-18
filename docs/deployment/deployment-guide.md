# 部署指南

## 版本信息
- 版本: v1.0
- 更新日期: 2025-06-18
- 状态: 就绪

## 部署架构概览

### 生产环境架构
```
Load Balancer (Nginx)
├── Admin Portal (3001)
├── Visitor Portal (3002) 
├── Employee Portal (3003)
├── Gate Portal (3004)
└── Reception Portal (3005)

API Gateway (Kong/Traefik)
└── Backend Services (8000)

Database Cluster
├── PostgreSQL Primary (5432)
├── PostgreSQL Replica (5433)
└── Redis Cluster (6379)

Message Queue
└── RabbitMQ (5672)

Monitoring Stack
├── Prometheus (9090)
├── Grafana (3000)
└── Jaeger (16686)
```

## 环境要求

### 硬件要求
**最小配置 (开发/测试)**:
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 100GB SSD
- 网络: 100Mbps

**推荐配置 (生产环境)**:
- CPU: 16核心
- 内存: 32GB RAM
- 存储: 500GB SSD
- 网络: 1Gbps

### 软件要求
- Docker 24.0+
- Docker Compose 2.20+
- Kubernetes 1.28+ (生产环境)
- Helm 3.12+ (Kubernetes部署)

## Docker部署

### 1. 环境配置
```bash
# 创建部署目录
mkdir visitor-management-deployment
cd visitor-management-deployment

# 创建环境变量文件
cat > .env << EOF
# 应用配置
NODE_ENV=production
API_BASE_URL=https://api.visitormgmt.com
FRONTEND_BASE_URL=https://visitormgmt.com

# 数据库配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=visitor_management
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=7d

# 文件存储
UPLOAD_PATH=/app/uploads
MAX_FILE_SIZE=10MB

# 邮件配置
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@visitormgmt.com
SMTP_PASSWORD=your_smtp_password

# 短信配置
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY=your_sms_access_key
SMS_SECRET_KEY=your_sms_secret_key
EOF
```

### 2. Docker Compose配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # 数据库服务
  postgres:
    image: postgres:15-alpine
    container_name: vm_postgres
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - vm_network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: vm_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - vm_network

  # 后端API服务
  backend:
    image: visitor-management/backend:latest
    container_name: vm_backend
    environment:
      - NODE_ENV=${NODE_ENV}
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - uploads:/app/uploads
      - logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - vm_network

  # 管理端
  admin-portal:
    image: visitor-management/admin-portal:latest
    container_name: vm_admin_portal
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_BASE_URL=${API_BASE_URL}
    ports:
      - "3001:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vm_network

  # 访客端
  visitor-portal:
    image: visitor-management/visitor-portal:latest
    container_name: vm_visitor_portal
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_BASE_URL=${API_BASE_URL}
    ports:
      - "3002:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vm_network

  # 员工端
  employee-portal:
    image: visitor-management/employee-portal:latest
    container_name: vm_employee_portal
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_BASE_URL=${API_BASE_URL}
    ports:
      - "3003:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vm_network

  # 门岗端
  gate-portal:
    image: visitor-management/gate-portal:latest
    container_name: vm_gate_portal
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_BASE_URL=${API_BASE_URL}
    ports:
      - "3004:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vm_network

  # 前台端
  reception-portal:
    image: visitor-management/reception-portal:latest
    container_name: vm_reception_portal
    environment:
      - NODE_ENV=${NODE_ENV}
      - API_BASE_URL=${API_BASE_URL}
    ports:
      - "3005:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - vm_network

  # Nginx负载均衡
  nginx:
    image: nginx:alpine
    container_name: vm_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - admin-portal
      - visitor-portal
      - employee-portal
      - gate-portal
      - reception-portal
      - backend
    restart: unless-stopped
    networks:
      - vm_network

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:

networks:
  vm_network:
    driver: bridge
```

### 3. Nginx配置
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream admin_backend {
        server admin-portal:80;
    }
    
    upstream visitor_backend {
        server visitor-portal:80;
    }
    
    upstream employee_backend {
        server employee-portal:80;
    }
    
    upstream gate_backend {
        server gate-portal:80;
    }
    
    upstream reception_backend {
        server reception-portal:80;
    }
    
    upstream api_backend {
        server backend:8000;
    }

    # 管理端
    server {
        listen 80;
        server_name admin.visitormgmt.com;
        return 301 https://$host$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name admin.visitormgmt.com;
        
        ssl_certificate /etc/nginx/ssl/admin.crt;
        ssl_certificate_key /etc/nginx/ssl/admin.key;
        
        location / {
            proxy_pass http://admin_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # 访客端
    server {
        listen 80;
        server_name visitor.visitormgmt.com;
        return 301 https://$host$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name visitor.visitormgmt.com;
        
        ssl_certificate /etc/nginx/ssl/visitor.crt;
        ssl_certificate_key /etc/nginx/ssl/visitor.key;
        
        location / {
            proxy_pass http://visitor_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # API网关
    server {
        listen 80;
        server_name api.visitormgmt.com;
        return 301 https://$host$request_uri;
    }
    
    server {
        listen 443 ssl;
        server_name api.visitormgmt.com;
        
        ssl_certificate /etc/nginx/ssl/api.crt;
        ssl_certificate_key /etc/nginx/ssl/api.key;
        
        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket支持
        location /ws {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

### 4. 部署脚本
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 开始部署访客管理系统..."

# 检查Docker环境
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要目录
mkdir -p ssl logs uploads init-scripts

# 生成SSL证书（开发环境）
if [ ! -f ssl/admin.crt ]; then
    echo "📜 生成SSL证书..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/admin.key -out ssl/admin.crt \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=VisitorMgmt/CN=admin.visitormgmt.com"
fi

# 拉取最新镜像
echo "📦 拉取Docker镜像..."
docker-compose pull

# 启动服务
echo "🔄 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 初始化数据库
echo "🗄️ 初始化数据库..."
docker-compose exec backend npm run migrate
docker-compose exec backend npm run seed

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

echo "✅ 部署完成！"
echo "🌐 访问地址："
echo "   管理端: https://admin.visitormgmt.com"
echo "   访客端: https://visitor.visitormgmt.com"
echo "   API: https://api.visitormgmt.com"
```

## Kubernetes部署

### 1. Helm Chart结构
```
charts/visitor-management/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── hpa.yaml
└── charts/
    ├── postgresql/
    └── redis/
```

### 2. Chart.yaml
```yaml
apiVersion: v2
name: visitor-management
description: 访客管理系统Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
  - name: redis
    version: 17.x.x
    repository: https://charts.bitnami.com/bitnami
```

### 3. values.yaml
```yaml
# 全局配置
global:
  imageRegistry: "your-registry.com"
  imageTag: "latest"
  storageClass: "fast-ssd"

# 应用配置
app:
  name: visitor-management
  namespace: visitor-mgmt
  replicas: 3
  
# 后端配置
backend:
  image:
    repository: visitor-management/backend
    tag: latest
  replicas: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "500m"

# 前端配置
frontend:
  adminPortal:
    image:
      repository: visitor-management/admin-portal
      tag: latest
    replicas: 2
    
  visitorPortal:
    image:
      repository: visitor-management/visitor-portal
      tag: latest
    replicas: 2

# 数据库配置
postgresql:
  enabled: true
  auth:
    postgresPassword: "your-postgres-password"
    database: "visitor_management"
  primary:
    persistence:
      enabled: true
      size: 100Gi
      storageClass: "fast-ssd"

# Redis配置
redis:
  enabled: true
  auth:
    password: "your-redis-password"
  master:
    persistence:
      enabled: true
      size: 10Gi

# Ingress配置
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: admin.visitormgmt.com
      paths:
        - path: /
          pathType: Prefix
          service: admin-portal
    - host: api.visitormgmt.com
      paths:
        - path: /
          pathType: Prefix
          service: backend
  tls:
    - secretName: visitormgmt-tls
      hosts:
        - admin.visitormgmt.com
        - api.visitormgmt.com

# 监控配置
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
  grafanaDashboard:
    enabled: true
```

### 4. 部署命令
```bash
# 添加依赖仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 创建命名空间
kubectl create namespace visitor-mgmt

# 安装Chart
helm install visitor-management ./charts/visitor-management \
  --namespace visitor-mgmt \
  --values values-production.yaml

# 升级部署
helm upgrade visitor-management ./charts/visitor-management \
  --namespace visitor-mgmt \
  --values values-production.yaml

# 查看状态
kubectl get pods -n visitor-mgmt
kubectl get services -n visitor-mgmt
kubectl get ingress -n visitor-mgmt
```

## 监控与日志

### 1. Prometheus配置
```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'visitor-management-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    
  - job_name: 'visitor-management-frontend'
    static_configs:
      - targets: ['admin-portal:80', 'visitor-portal:80']
    metrics_path: /metrics

rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 2. Grafana仪表板
```json
{
  "dashboard": {
    "title": "访客管理系统监控",
    "panels": [
      {
        "title": "API响应时间",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "访客统计",
        "type": "stat",
        "targets": [
          {
            "expr": "visitors_total"
          }
        ]
      }
    ]
  }
}
```

## 安全配置

### 1. 网络安全
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: visitor-management-network-policy
  namespace: visitor-mgmt
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: visitor-mgmt
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
```

### 2. 密钥管理
```bash
# 创建TLS密钥
kubectl create secret tls visitormgmt-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  --namespace visitor-mgmt

# 创建应用密钥
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret=your-jwt-secret \
  --from-literal=db-password=your-db-password \
  --from-literal=redis-password=your-redis-password \
  --namespace visitor-mgmt
```

## 备份与恢复

### 1. 数据库备份
```bash
#!/bin/bash
# backup.sh

NAMESPACE="visitor-mgmt"
DB_POD=$(kubectl get pod -n $NAMESPACE -l app=postgresql -o jsonpath='{.items[0].metadata.name}')

# 创建备份
kubectl exec -n $NAMESPACE $DB_POD -- pg_dump \
  -U postgres visitor_management \
  > backup_$(date +%Y%m%d_%H%M%S).sql

# 上传到对象存储
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql \
  s3://visitor-mgmt-backups/
```

### 2. 应用配置备份
```bash
# 备份Kubernetes配置
kubectl get all,configmap,secret,ingress -n visitor-mgmt -o yaml \
  > k8s-backup-$(date +%Y%m%d).yaml
```

## 性能优化

### 1. 自动扩缩容
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: visitor-mgmt
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. 缓存优化
```yaml
# redis-cluster.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6
  template:
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - /conf/redis.conf
        - --cluster-enabled
        - "yes"
        - --cluster-config-file
        - nodes.conf
        - --cluster-node-timeout
        - "5000"
```

## 故障排查

### 常见问题及解决方案

1. **服务无法启动**
```bash
# 检查Pod状态
kubectl describe pod -n visitor-mgmt

# 查看日志
kubectl logs -f deployment/backend -n visitor-mgmt

# 检查配置
kubectl get configmap -n visitor-mgmt -o yaml
```

2. **数据库连接失败**
```bash
# 检查数据库Pod状态
kubectl get pod -l app=postgresql -n visitor-mgmt

# 测试数据库连接
kubectl exec -it deployment/backend -n visitor-mgmt -- \
  psql -h postgresql -U postgres -d visitor_management
```

3. **前端无法访问API**
```bash
# 检查Ingress配置
kubectl get ingress -n visitor-mgmt
kubectl describe ingress visitormgmt-ingress -n visitor-mgmt

# 检查Service
kubectl get svc -n visitor-mgmt
```

## 部署检查清单

### 部署前检查
- [ ] 环境变量配置完整
- [ ] SSL证书有效
- [ ] 镜像版本正确
- [ ] 数据库连接配置正确
- [ ] 存储空间充足

### 部署后验证
- [ ] 所有Pod状态为Running
- [ ] 服务可以正常访问
- [ ] 数据库连接正常
- [ ] API接口响应正常
- [ ] 前端页面加载正常
- [ ] WebSocket连接正常
- [ ] 监控指标正常
- [ ] 日志收集正常

本部署指南提供了完整的Docker和Kubernetes部署方案，支持从开发环境到生产环境的平滑过渡，并包含了监控、安全、备份等生产环境必需的组件配置。 