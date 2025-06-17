# 数据库迁移指南

## 📋 文档信息
- **版本**: v2.0.0
- **创建日期**: 2025-06-17
- **最后更新**: 2025-06-17
- **适用角色**: DBA、运维工程师、后端开发者

## 🎯 迁移概述

访客管理系统使用Alembic进行数据库版本控制和迁移管理，支持自动化的数据库结构变更和数据迁移。

### 迁移特性
- ✅ **版本控制**: 每次变更都有唯一版本号
- ✅ **自动化**: 支持自动执行迁移脚本
- ✅ **回滚支持**: 支持降级到历史版本
- ✅ **数据安全**: 变更前自动备份
- ✅ **环境隔离**: 不同环境独立迁移

## 🚀 快速迁移

### 执行迁移
```bash
# 升级到最新版本
alembic upgrade head

# 升级到指定版本
alembic upgrade 20250608_120000

# 降级到上一版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

### 生成新迁移
```bash
# 自动生成迁移脚本
alembic revision --autogenerate -m "添加访客评分字段"

# 手动创建空迁移脚本
alembic revision -m "自定义数据迁移"
```

## 📊 迁移版本历史

### 当前版本概览
| 版本号 | 日期 | 描述 | 状态 |
|--------|------|------|------|
| 20250617_143000 | 2025-06-17 | 配置引擎审计字段 | ✅ 已应用 |
| 20250608_120000 | 2025-06-08 | 配置引擎表创建 | ✅ 已应用 |
| 20250607_210000 | 2025-06-07 | 访客状态枚举完善 | ✅ 已应用 |
| 20250607_203857 | 2025-06-07 | 数据库性能优化 | ✅ 已应用 |

### 版本详细信息

#### v20250617_143000 - 配置引擎审计字段迁移
**变更内容**:
- 为form_configurations表添加审计字段
- 为workflow_configurations表添加审计字段
- 为spatial_configurations表添加审计字段
- 为business_rules表添加审计字段
- 创建软删除索引

**影响评估**:
- 表结构变更: 4个表
- 新增索引: 8个
- 数据迁移: 无
- 停机时间: < 5分钟

#### v20250608_120000 - 配置引擎表创建
**变更内容**:
- 创建form_configurations表
- 创建form_field_configurations表
- 创建workflow_configurations表
- 创建spatial_configurations表
- 创建business_rules表

## 🛠️ 迁移操作指南

### 1. 生产环境迁移流程

#### 迁移前检查
```bash
# 1. 检查当前数据库状态
alembic current

# 2. 验证迁移脚本
alembic show <revision_id>

# 3. 模拟迁移（空运行）
alembic upgrade <revision_id> --sql > migration_preview.sql

# 4. 检查数据库连接
psql $DATABASE_URL -c "SELECT 1"
```

#### 生产迁移步骤
```bash
# 1. 创建数据备份
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. 停止应用服务（如需要）
systemctl stop visitor-management

# 3. 执行迁移
alembic upgrade head

# 4. 验证迁移结果
python verify_migration.py

# 5. 重启应用服务
systemctl start visitor-management

# 6. 验证应用功能
curl http://localhost:8000/health
```

### 2. 回滚操作

#### 紧急回滚
```bash
# 1. 停止应用
systemctl stop visitor-management

# 2. 回滚到安全版本
alembic downgrade <safe_revision>

# 3. 恢复数据（如需要）
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql

# 4. 重启应用
systemctl start visitor-management
```

### 3. 迁移脚本编写

#### 标准迁移脚本模板
```python
"""添加访客评分字段

Revision ID: 20250618_100000
Revises: 20250617_143000
Create Date: 2025-06-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20250618_100000'
down_revision = '20250617_143000'
branch_labels = None
depends_on = None

def upgrade():
    """升级操作"""
    # 1. 添加新字段
    op.add_column('visitors', sa.Column('rating', sa.Integer(), nullable=True))
    
    # 2. 创建索引
    op.create_index('idx_visitors_rating', 'visitors', ['rating'])
    
    # 3. 更新现有数据
    connection = op.get_bind()
    connection.execute(
        "UPDATE visitors SET rating = 5 WHERE status = 'completed'"
    )

def downgrade():
    """降级操作"""
    # 1. 删除索引
    op.drop_index('idx_visitors_rating', 'visitors')
    
    # 2. 删除字段
    op.drop_column('visitors', 'rating')
```

#### 数据迁移脚本示例
```python
def upgrade():
    """数据迁移示例"""
    # 获取数据库连接
    connection = op.get_bind()
    
    # 1. 批量数据更新
    connection.execute("""
        UPDATE employees 
        SET status = 'active' 
        WHERE status IS NULL 
          AND hire_date < CURRENT_DATE
    """)
    
    # 2. 数据转换
    result = connection.execute("SELECT id, old_field FROM legacy_table")
    for row in result:
        new_value = transform_data(row.old_field)
        connection.execute(
            "UPDATE new_table SET new_field = %s WHERE id = %s",
            (new_value, row.id)
        )
    
    # 3. 添加约束
    op.alter_column('employees', 'status', nullable=False)
```

## 🔍 迁移验证

### 自动验证脚本
```python
# verify_migration.py
import asyncio
import asyncpg
from sqlalchemy import create_engine, text

async def verify_migration():
    """验证迁移结果"""
    print("🔍 开始验证数据库迁移...")
    
    # 连接数据库
    engine = create_engine(DATABASE_URL)
    
    # 验证表结构
    checks = [
        verify_table_exists,
        verify_columns_exist,
        verify_indexes_exist,
        verify_constraints_exist,
        verify_data_integrity
    ]
    
    for check in checks:
        try:
            await check(engine)
            print(f"✅ {check.__name__} 通过")
        except Exception as e:
            print(f"❌ {check.__name__} 失败: {e}")
            return False
    
    print("🎉 数据库迁移验证完成")
    return True

async def verify_table_exists(engine):
    """验证表是否存在"""
    required_tables = [
        'visitors', 'employees', 'departments', 'sites',
        'form_configurations', 'workflow_configurations'
    ]
    
    with engine.connect() as conn:
        for table in required_tables:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = :table_name
                )
            """), {"table_name": table})
            
            if not result.scalar():
                raise Exception(f"表 {table} 不存在")

async def verify_columns_exist(engine):
    """验证列是否存在"""
    column_checks = [
        ('form_configurations', 'is_deleted'),
        ('workflow_configurations', 'deleted_at'),
        ('visitors', 'tenant_id'),
    ]
    
    with engine.connect() as conn:
        for table, column in column_checks:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = :table_name 
                      AND column_name = :column_name
                )
            """), {"table_name": table, "column_name": column})
            
            if not result.scalar():
                raise Exception(f"表 {table} 缺少列 {column}")

if __name__ == "__main__":
    asyncio.run(verify_migration())
```

### 性能验证
```python
# performance_check.py
import time
from sqlalchemy import create_engine, text

def check_query_performance():
    """检查关键查询性能"""
    engine = create_engine(DATABASE_URL)
    
    queries = [
        ("访客列表查询", """
            SELECT * FROM visitors 
            WHERE tenant_id = 'default' 
              AND is_deleted = false 
            LIMIT 20
        """),
        ("配置表查询", """
            SELECT * FROM form_configurations 
            WHERE tenant_id = 'default' 
              AND is_active = true
        """),
    ]
    
    with engine.connect() as conn:
        for name, query in queries:
            start_time = time.time()
            result = conn.execute(text(query))
            list(result)  # 消费结果
            execution_time = time.time() - start_time
            
            print(f"{name}: {execution_time:.3f}s")
            if execution_time > 1.0:
                print(f"⚠️ {name} 性能较慢")
```

## ⚠️ 注意事项

### 迁移安全原则
1. **备份优先**: 迁移前必须备份数据
2. **测试先行**: 在测试环境充分验证
3. **分步执行**: 大型迁移分多个步骤
4. **可回滚**: 确保每个迁移都可回滚
5. **监控告警**: 迁移期间监控系统状态

### 常见问题处理

#### 迁移失败处理
```bash
# 查看迁移错误详情
alembic history --verbose

# 手动标记版本（仅在确认数据正确时使用）
alembic stamp <revision_id>

# 重置迁移状态
alembic stamp base
alembic upgrade head
```

#### 数据冲突解决
```sql
-- 处理唯一约束冲突
UPDATE employees SET employee_id = employee_id || '_dup' 
WHERE id IN (
    SELECT id FROM (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY id) as rn
        FROM employees
    ) t WHERE rn > 1
);
```

### 大数据量迁移策略

#### 分批迁移
```python
def upgrade():
    """大数据量分批迁移"""
    connection = op.get_bind()
    
    batch_size = 10000
    offset = 0
    
    while True:
        result = connection.execute(f"""
            SELECT id, old_field 
            FROM large_table 
            ORDER BY id 
            LIMIT {batch_size} OFFSET {offset}
        """)
        
        rows = result.fetchall()
        if not rows:
            break
            
        # 批量更新
        updates = []
        for row in rows:
            new_value = transform_data(row.old_field)
            updates.append((new_value, row.id))
        
        connection.execute(
            "UPDATE large_table SET new_field = %s WHERE id = %s",
            updates
        )
        
        offset += batch_size
        print(f"已处理 {offset} 条记录")
```

## 📊 监控和告警

### 迁移监控脚本
```bash
#!/bin/bash
# migration_monitor.sh

echo "🔍 开始迁移监控..."

# 检查数据库连接
if ! psql $DATABASE_URL -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ 数据库连接失败"
    exit 1
fi

# 检查当前迁移版本
current_version=$(alembic current)
echo "📍 当前版本: $current_version"

# 检查待执行迁移
pending=$(alembic heads)
echo "⏳ 最新版本: $pending"

# 检查表结构完整性
python verify_migration.py

echo "✅ 监控检查完成"
```

---

## 📞 技术支持

### 迁移支持
- **负责人**: 数据库管理员
- **紧急联系**: DBA值班电话
- **文档更新**: 随迁移版本更新

### 相关文档
- [后端数据模型设计文档](./Backend_Data_Models.md)
- [后端系统架构概览](./Backend_System_Architecture.md)
- [后端开发者指南](./Backend_Developer_Guide.md) 