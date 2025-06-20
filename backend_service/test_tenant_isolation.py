#!/usr/bin/env python3
"""
租户隔离测试脚本
验证多租户数据隔离是否正确工作
"""
import asyncio
import httpx
import json


class TenantIsolationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_token = None
    
    async def authenticate(self, client: httpx.AsyncClient) -> bool:
        """管理员认证"""
        try:
            response = await client.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print("✅ 管理员认证成功")
                return True
            else:
                print(f"❌ 认证失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 认证异常: {e}")
            return False
    
    async def create_visitor_with_tenant(self, client: httpx.AsyncClient, tenant_override: str = None) -> dict:
        """创建访客记录（可指定租户）"""
        visitor_data = {
            "name": f"租户隔离测试访客-{tenant_override or 'default'}",
            "phone_number": "13999999999",
            "identification_no": "999999999999999999",
            "company_name": "租户测试公司", 
            "purpose": "business",
            "expected_date": "2025-06-21T14:00:00",
            "employee_id": 1,
            "site_id": 5
        }
        
        # 使用匿名申请API（无认证）
        response = await client.post(
            f"{self.base_url}/api/v1/visitors/apply",
            json=visitor_data
        )
        
        if response.status_code == 200:
            visitor = response.json()
            print(f"✅ 创建访客成功: ID={visitor['id']}, 租户={visitor['tenant_id']}, 姓名={visitor['name']}")
            return visitor
        else:
            print(f"❌ 创建访客失败: {response.status_code}, {response.text}")
            return None
    
    async def get_visitors_with_auth(self, client: httpx.AsyncClient) -> list:
        """使用认证获取访客列表"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = await client.get(
            f"{self.base_url}/api/v1/visitors/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            visitors = data["items"]
            print(f"✅ 认证访客列表获取成功: 共{len(visitors)}条记录")
            return visitors
        else:
            print(f"❌ 获取访客列表失败: {response.status_code}")
            return []
    
    async def query_by_phone_anonymous(self, client: httpx.AsyncClient, phone: str) -> list:
        """匿名通过手机号查询"""
        response = await client.get(
            f"{self.base_url}/api/v1/visitors/query/by-phone?phone_number={phone}"
        )
        
        if response.status_code == 200:
            visitors = response.json()
            print(f"✅ 匿名手机号查询成功: 共{len(visitors)}条记录")
            return visitors
        else:
            print(f"❌ 匿名手机号查询失败: {response.status_code}")
            return []
    
    async def test_tenant_isolation(self):
        """测试租户隔离"""
        print("🔒 开始租户隔离测试...")
        
        async with httpx.AsyncClient() as client:
            # 1. 管理员认证
            if not await self.authenticate(client):
                return
            
            # 2. 创建匿名访客（应该分配到default租户）
            anonymous_visitor = await self.create_visitor_with_tenant(client)
            if not anonymous_visitor:
                return
            
            # 3. 通过认证API获取访客列表（应该看到default租户的访客）
            auth_visitors = await self.get_visitors_with_auth(client)
            
            # 4. 通过匿名手机号查询（应该只能查到default租户的访客）
            phone_visitors = await self.query_by_phone_anonymous(client, "13999999999")
            
            # 5. 分析租户隔离情况
            await self.analyze_isolation(anonymous_visitor, auth_visitors, phone_visitors)
    
    async def analyze_isolation(self, anonymous_visitor: dict, auth_visitors: list, phone_visitors: list):
        """分析租户隔离情况"""
        print("\n📊 租户隔离分析:")
        
        # 检查匿名创建的访客租户
        print(f"1. 匿名访客租户ID: {anonymous_visitor['tenant_id']}")
        if anonymous_visitor['tenant_id'] == 'default':
            print("   ✅ 匿名访客正确分配到default租户")
        else:
            print(f"   ❌ 匿名访客租户错误，应该是'default'")
        
        # 检查认证API返回的访客租户
        default_count = sum(1 for v in auth_visitors if v['tenant_id'] == 'default')
        other_tenants = set(v['tenant_id'] for v in auth_visitors if v['tenant_id'] != 'default')
        
        print(f"2. 认证API访客列表: 总数{len(auth_visitors)}, default租户{default_count}条")
        if other_tenants:
            print(f"   ⚠️  发现其他租户数据: {other_tenants}")
        else:
            print("   ✅ 认证API只返回了default租户数据")
        
        # 检查手机号查询的租户隔离
        phone_default_count = sum(1 for v in phone_visitors if v['tenant_id'] == 'default')
        phone_other_tenants = set(v['tenant_id'] for v in phone_visitors if v['tenant_id'] != 'default')
        
        print(f"3. 手机号查询结果: 总数{len(phone_visitors)}, default租户{phone_default_count}条")
        if phone_other_tenants:
            print(f"   ❌ 手机号查询泄露了其他租户数据: {phone_other_tenants}")
        else:
            print("   ✅ 手机号查询正确隔离了租户数据")
        
        # 验证数据一致性
        found_anonymous = any(v['id'] == anonymous_visitor['id'] for v in auth_visitors)
        found_in_phone = any(v['id'] == anonymous_visitor['id'] for v in phone_visitors)
        
        print(f"4. 数据一致性检查:")
        print(f"   认证API能找到匿名创建的访客: {'✅ 是' if found_anonymous else '❌ 否'}")
        print(f"   手机号查询能找到匿名创建的访客: {'✅ 是' if found_in_phone else '❌ 否'}")
        
        # 总结
        isolation_ok = (
            anonymous_visitor['tenant_id'] == 'default' and
            len(other_tenants) == 0 and 
            len(phone_other_tenants) == 0 and
            found_anonymous and found_in_phone
        )
        
        print(f"\n🎯 租户隔离测试结果: {'✅ 通过' if isolation_ok else '❌ 失败'}")
        
        if isolation_ok:
            print("   所有API都正确实现了租户数据隔离")
        else:
            print("   发现租户隔离问题，需要进一步检查")


async def main():
    tester = TenantIsolationTester()
    await tester.test_tenant_isolation()


if __name__ == "__main__":
    asyncio.run(main()) 