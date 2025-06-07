#!/usr/bin/env python3
"""
调试站点创建问题
"""

import asyncio
import sys
sys.path.append('.')

from app.infrastructure.database.connection import get_db
from app.application.services.site_service import SiteService
from app.application.dto.site_dto import SiteCreateDTO

async def test_site_creation():
    """测试站点创建"""
    async for db in get_db():
        try:
            service = SiteService(db)
            
            import time
            site_data = SiteCreateDTO(
                name="测试站点",
                code=f"TEST_{int(time.time())}",
                address="测试地址123号",
                description="测试站点"
            )
            
            print("开始创建站点...")
            result = await service.create_site(site_data, "admin", "default")
            print(f"创建成功: {result}")
            
        except Exception as e:
            print(f"创建失败: {e}")
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_site_creation()) 