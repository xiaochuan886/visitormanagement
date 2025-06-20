# 访客管理系统门岗前台功能测试指南

## 🧪 测试概览

本指南将帮助您全面测试门岗前台功能的各个组件，确保系统正常运行。

### 测试环境要求
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (推荐)

## 🚀 快速启动测试

### 方法1: Docker Compose 部署（推荐）

```bash
# 1. 启动完整测试环境（包含模拟器）
docker-compose -f docker-compose.gate-reception.yml --profile simulators --profile monitoring up -d

# 2. 等待服务启动（约30-60秒）
docker-compose -f docker-compose.gate-reception.yml ps

# 3. 检查服务健康状态
curl http://localhost/api/v1/health
```

### 方法2: 本地开发环境

```bash
# 1. 安装依赖
cd backend_service
pip install -r requirements.txt

# 2. 启动数据库服务
docker-compose up -d postgres redis

# 3. 运行数据库迁移
alembic upgrade head

# 4. 启动应用
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. 验证启动
curl http://localhost:8000/api/v1/health
```

## 📋 系统功能测试清单

### 1. 基础系统测试

#### 1.1 健康检查测试
```bash
# 系统整体健康检查
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "accept: application/json"

# 数据库健康检查
curl -X GET "http://localhost:8000/api/v1/health/database" \
  -H "accept: application/json"

# 服务组件健康检查
curl -X GET "http://localhost:8000/api/v1/health/services" \
  -H "accept: application/json"

# 设备状态健康检查
curl -X GET "http://localhost:8000/api/v1/health/devices" \
  -H "accept: application/json"
```

#### 1.2 认证测试
```bash
# 获取访问令牌
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 保存返回的access_token，后续请求需要使用
export ACCESS_TOKEN="your_access_token_here"
```

### 2. 设备管理测试

#### 2.1 设备注册测试
```bash
# 注册门岗设备
curl -X POST "http://localhost:8000/api/v1/devices/register" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "GATE001",
    "device_name": "主门岗终端",
    "device_type": "gate_terminal",
    "location": "主入口",
    "ip_address": "192.168.1.100",
    "capabilities": ["qr_scan", "face_recognition", "id_card_reader"]
  }'

# 注册前台设备
curl -X POST "http://localhost:8000/api/v1/devices/register" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RECEPTION001", 
    "device_name": "前台接待终端",
    "device_type": "reception_kiosk",
    "location": "前台大厅",
    "ip_address": "192.168.1.101"
  }'

# 注册移动设备
curl -X POST "http://localhost:8000/api/v1/devices/register" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "MOBILE001",
    "device_name": "移动验证终端",
    "device_type": "mobile_tablet", 
    "location": "巡检使用",
    "ip_address": "192.168.1.102"
  }'
```

#### 2.2 设备状态更新测试
```bash
# 更新设备状态
curl -X POST "http://localhost:8000/api/v1/devices/GATE001/status" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "online",
    "cpu_usage": 45.2,
    "memory_usage": 68.1,
    "disk_usage": 32.5,
    "temperature": 42.0
  }'
```

#### 2.3 设备列表查询测试
```bash
# 获取设备列表
curl -X GET "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 获取设备详情
curl -X GET "http://localhost:8000/api/v1/devices/GATE001" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 3. 访客预约测试

#### 3.1 创建访客预约
```bash
# 创建访客预约
curl -X POST "http://localhost:8000/api/v1/visitors" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "phone": "13800138001", 
    "id_card": "110101199001011234",
    "company": "测试公司",
    "visit_purpose": "商务洽谈",
    "host_name": "李四",
    "host_phone": "13800138002",
    "visit_date": "'$(date -d '+1 day' -Iseconds)'",
    "expected_duration": 120,
    "vehicle_plate": "京A12345"
  }'
```

### 4. 门岗验证功能测试

#### 4.1 二维码验证测试
```bash
# 门岗二维码验证
curl -X POST "http://localhost:8000/api/v1/gate/verify-visitor" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "device_id": "GATE001",
    "verification_method": "qr_code",
    "verification_data": {
      "qr_code": "VIS_QR_001_'$(date +%s)'",
      "scan_time": "'$(date -Iseconds)'"
    }
  }'
```

#### 4.2 身份证验证测试
```bash
# 门岗身份证验证
curl -X POST "http://localhost:8000/api/v1/gate/verify-visitor" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "device_id": "GATE001", 
    "verification_method": "id_card",
    "verification_data": {
      "id_number": "110101199001011234",
      "scan_time": "'$(date -Iseconds)'"
    }
  }'
```

#### 4.3 人脸识别验证测试
```bash
# 门岗人脸识别验证
curl -X POST "http://localhost:8000/api/v1/gate/verify-visitor" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "device_id": "GATE001",
    "verification_method": "face_recognition", 
    "verification_data": {
      "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "confidence": 95.5
    }
  }'
```

#### 4.4 访客入园测试
```bash
# 访客入园记录
curl -X POST "http://localhost:8000/api/v1/gate/visitor-entry" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "gate_id": "GATE001",
    "entry_photo_url": "https://example.com/photos/entry_001.jpg",
    "badge_number": "V001",
    "vehicle_plate": "京A12345",
    "temperature_check": 36.5,
    "health_check_passed": true
  }'
```

#### 4.5 今日访客查询测试
```bash
# 获取今日访客列表
curl -X GET "http://localhost:8000/api/v1/gate/today-visitors?gate_id=GATE001" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 获取访客缓存
curl -X GET "http://localhost:8000/api/v1/gate/visitor-cache?device_id=GATE001" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 5. 前台签到功能测试

#### 5.1 访客签到测试
```bash
# 前台访客签到
curl -X POST "http://localhost:8000/api/v1/reception/visitor-checkin" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "reception_desk_id": "RECEPTION001",
    "checkin_method": "manual",
    "waiting_area_id": "WAIT_AREA_A",
    "services_provided": ["身份验证", "访客登记", "等候安排"]
  }'
```

#### 5.2 主机通知测试
```bash
# 通知主机
curl -X POST "http://localhost:8000/api/v1/reception/notify-host" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "visitor_id": 1,
    "employee_id": 1,
    "notification_channels": ["wechat", "email"],
    "notification_content": {
      "title": "访客到访通知",
      "message": "您的访客张三已到达前台",
      "visitor_info": {
        "name": "张三",
        "company": "测试公司", 
        "purpose": "商务洽谈"
      }
    }
  }'
```

#### 5.3 等候区域状态测试
```bash
# 获取等候区域状态
curl -X GET "http://localhost:8000/api/v1/reception/waiting-area/status" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 获取前台工作台状态
curl -X GET "http://localhost:8000/api/v1/reception/dashboard" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### 5.4 会议室管理测试
```bash
# 创建会议室
curl -X POST "http://localhost:8000/api/v1/reception/meeting-rooms" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "会议室A",
    "room_code": "ROOM_A001",
    "capacity": 10,
    "location": "3楼西侧",
    "amenities": ["投影仪", "白板", "网络"],
    "booking_rules": {
      "advance_booking_days": 7,
      "max_booking_hours": 4,
      "min_booking_minutes": 30
    }
  }'

# 预订会议室
curl -X POST "http://localhost:8000/api/v1/reception/meeting-room-bookings" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "visitor_id": 1,
    "start_time": "'$(date -d '+1 hour' -Iseconds)'",
    "end_time": "'$(date -d '+3 hours' -Iseconds)'",
    "meeting_title": "项目讨论会",
    "attendee_count": 5
  }'
```

### 6. 移动端同步测试

#### 6.1 数据同步测试
```bash
# 移动端数据同步
curl -X POST "http://localhost:8000/api/v1/mobile/sync-data" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "MOBILE001",
    "sync_type": "incremental_sync",
    "data_types": ["visitors", "verifications"],
    "last_sync_time": "'$(date -d '-1 hour' -Iseconds)'",
    "network_quality": "good"
  }'
```

#### 6.2 离线验证上传测试
```bash
# 上传离线验证记录
curl -X POST "http://localhost:8000/api/v1/mobile/upload-offline-verifications" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "verifications": [
      {
        "visitor_id": 1,
        "device_id": "MOBILE001",
        "verification_method": "qr_code",
        "verification_data": {"qr_code": "OFFLINE_QR_001"},
        "offline_time": "'$(date -d '-30 minutes' -Iseconds)'",
        "device_timestamp": "'$(date -d '-30 minutes' -Iseconds)'"
      }
    ]
  }'
```

#### 6.3 应急验证测试
```bash
# 应急验证处理
curl -X POST "http://localhost:8000/api/v1/mobile/emergency-verification" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "emergency_type": "system_failure",
    "reason": "网络中断",
    "affected_devices": ["GATE001", "GATE002"],
    "operation_type": "enable_offline_mode",
    "operator": "应急响应员"
  }'
```

## 🧾 自动化测试

### 运行集成测试套件
```bash
# 运行完整的集成测试
cd backend_service
python -m pytest tests/test_gate_reception_integration.py -v

# 运行特定测试
python -m pytest tests/test_gate_reception_integration.py::TestGateReceptionIntegration::test_complete_visitor_flow -v

# 生成测试报告
python -m pytest tests/test_gate_reception_integration.py --html=test_report.html
```

### API文档生成和验证
```bash
# 生成API文档
cd scripts
python update_api_docs.py

# 验证生成的文档
ls -la ../docs/api/
```

## 📊 性能测试

### 基准性能测试
```bash
# 使用Apache Bench进行压力测试
# 健康检查端点
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# 设备列表查询（需要认证）
ab -n 500 -c 5 -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/v1/devices

# 门岗验证接口
ab -n 100 -c 5 -p verify_data.json -T application/json -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/v1/gate/verify-visitor
```

### 数据库性能测试
```bash
# 查看数据库连接数
docker exec visitor-management-postgres psql -U postgres -d visitor_management -c "SELECT count(*) FROM pg_stat_activity;"

# 查看表大小
docker exec visitor-management-postgres psql -U postgres -d visitor_management -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

## 🔍 监控和日志

### 查看应用日志
```bash
# 查看主应用日志
docker-compose -f docker-compose.gate-reception.yml logs -f visitor-management-app

# 查看数据库日志
docker-compose -f docker-compose.gate-reception.yml logs -f postgres

# 查看Redis日志
docker-compose -f docker-compose.gate-reception.yml logs -f redis
```

### 监控面板访问
- **Grafana监控**: http://localhost:3000 (admin/admin123)
- **Prometheus指标**: http://localhost:9090
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

### 指标监控
```bash
# 查看系统指标
curl -X GET "http://localhost:8000/api/v1/health/metrics" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 查看设备使用统计
curl -X GET "http://localhost:8000/api/v1/devices/GATE001/usage-stats?start_date=2024-12-01&end_date=2024-12-31" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## ❗ 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查数据库状态
docker-compose -f docker-compose.gate-reception.yml ps postgres
docker-compose -f docker-compose.gate-reception.yml logs postgres

# 重启数据库
docker-compose -f docker-compose.gate-reception.yml restart postgres
```

#### 2. Redis连接失败
```bash
# 检查Redis状态
docker-compose -f docker-compose.gate-reception.yml ps redis
docker-compose -f docker-compose.gate-reception.yml logs redis

# 测试Redis连接
docker exec visitor-management-redis redis-cli ping
```

#### 3. API认证失败
```bash
# 检查JWT配置
echo $ACCESS_TOKEN | base64 -d

# 重新获取令牌
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### 4. 设备注册失败
```bash
# 检查设备状态
curl -X GET "http://localhost:8000/api/v1/devices" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 查看设备日志
curl -X GET "http://localhost:8000/api/v1/devices/GATE001/status-logs" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
export LOG_LEVEL=DEBUG

# 重启应用
docker-compose -f docker-compose.gate-reception.yml restart visitor-management-app
```

## ✅ 测试验收标准

### 功能验收
- [ ] 所有健康检查接口返回正常状态
- [ ] 设备注册、状态更新、配置管理功能正常
- [ ] 门岗验证的5种方法都能正常工作
- [ ] 前台签到、通知、会议室管理功能正常
- [ ] 移动端数据同步、离线验证功能正常
- [ ] 应急处理和故障切换机制正常

### 性能验收
- [ ] API响应时间 < 500ms (P95)
- [ ] 数据库查询时间 < 100ms (P95)
- [ ] 系统可支持100并发用户
- [ ] 内存使用率 < 80%
- [ ] CPU使用率 < 70%

### 安全验收
- [ ] 所有API需要有效认证
- [ ] 敏感数据正确加密存储
- [ ] 访问日志完整记录
- [ ] 权限控制正确生效

## 📞 测试支持

如果在测试过程中遇到问题，请：

1. 查看本指南的故障排除部分
2. 检查应用日志和系统状态
3. 确认测试数据的正确性
4. 验证网络连接和服务依赖

**测试完成后**，请提供测试结果反馈，包括：
- 功能测试通过情况
- 性能测试结果
- 发现的问题和建议
- 改进意见

祝测试顺利！🚀 