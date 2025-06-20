#!/usr/bin/env python3
"""
匿名访客租户ID传递策略分析
详细分析前端和后端实现方案
"""

def analyze_tenant_strategies():
    """分析多种租户ID传递策略"""
    
    print("=" * 80)
    print("🏠 匿名访客租户ID传递策略分析")
    print("=" * 80)
    
    # 当前实现
    print("\n## 🔄 当前实现：后端默认租户分配")
    print("-" * 50)
    print("实现位置: 后端自动分配")
    print("传递机制: 无需前端参与")
    print("代码位置: app/api/dependencies/tenant.py")
    print("""
关键代码:
async def get_current_tenant_optional(current_user=None) -> str:
    if current_user and current_user.get("tenant_id"):
        return current_user["tenant_id"]  # 认证用户租户
    return settings.default_tenant_id or "default"  # 匿名默认租户
    """)
    print("✅ 优点: 简单、向下兼容、无需前端配合")
    print("❌ 缺点: 无法区分访问来源、所有匿名申请混合")
    
    # Header方案
    print("\n## 📋 方案1：HTTP Header传递")
    print("-" * 50)
    print("实现位置: 前端Header + 后端解析")
    print("传递机制: X-Tenant-ID Header")
    print("""
前端实现:
fetch('/api/v1/visitors/apply', {
    headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': 'company_a'  // 前端指定租户
    },
    body: JSON.stringify(data)
});

后端实现:
@router.post("/apply")
async def apply_visitor(
    visitor_data: VisitorCreateDTO,
    tenant_id: str = Header(None, alias="X-Tenant-ID")
):
    final_tenant = tenant_id or "default"
    """)
    print("✅ 优点: 灵活、支持多租户、HTTP标准")
    print("❌ 缺点: 需前端配合、存在伪造风险")
    
    # 域名方案
    print("\n## 🌐 方案2：域名自动识别")
    print("-" * 50)
    print("实现位置: 后端中间件解析")
    print("传递机制: 子域名或独立域名")
    print("""
域名映射:
company-a.visitor.com → company_a
company-b.visitor.com → company_b
visitor.company-a.com → company_a

后端实现:
async def get_tenant_from_domain(request: Request) -> str:
    host = request.headers.get("host", "")
    if host.endswith(".visitor.com"):
        return host.split(".")[0]  # 提取子域名
    return domain_map.get(host, "default")
    """)
    print("✅ 优点: 用户体验佳、无法伪造、天然多品牌")
    print("❌ 缺点: DNS配置复杂、部署成本高")
    
    # URL路径方案
    print("\n## 🛣️ 方案3：URL路径参数")
    print("-" * 50)
    print("实现位置: 路由层面解析")
    print("传递机制: URL路径包含租户ID")
    print("""
API路径:
/api/v1/company-a/visitors/apply → company_a
/api/v1/company-b/visitors/apply → company_b
/api/v1/visitors/apply → default

后端实现:
@router.post("/{tenant_id}/visitors/apply")
async def apply_visitor_with_tenant(
    tenant_id: str,
    visitor_data: VisitorCreateDTO
):
    if tenant_id not in VALID_TENANTS:
        raise HTTPException(404)
    """)
    print("✅ 优点: URL语义清晰、易于理解和调试")
    print("❌ 缺点: URL复杂、需要维护多套路由")
    
    # 查询参数方案
    print("\n## ❓ 方案4：查询参数传递")
    print("-" * 50)
    print("实现位置: 前端URL + 后端解析")
    print("传递机制: ?tenant=xxx查询参数")
    print("""
API调用:
/api/v1/visitors/apply?tenant=company_a
/api/v1/visitors/apply?tenant=company_b
/api/v1/visitors/apply (默认租户)

前端实现:
const url = tenantId 
    ? `/api/v1/visitors/apply?tenant=${tenantId}`
    : `/api/v1/visitors/apply`;

后端实现:
@router.post("/apply")
async def apply_visitor(
    visitor_data: VisitorCreateDTO,
    tenant: Optional[str] = Query(None)
):
    tenant_id = tenant if tenant in VALID_TENANTS else "default"
    """)
    print("✅ 优点: 实现简单、向下兼容、URL可见")
    print("❌ 缺点: 租户信息暴露、可能被缓存")
    
    # 推荐方案
    print("\n## 🎯 推荐策略组合")
    print("-" * 50)
    print("🏢 企业内部系统: 当前实现(默认租户) + Header方案")
    print("🌐 SaaS多租户: 域名方案 + Header备选")
    print("📱 移动应用: Header方案 + 查询参数备选")
    print("🔧 开发测试: 查询参数方案(便于调试)")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_tenant_strategies() 