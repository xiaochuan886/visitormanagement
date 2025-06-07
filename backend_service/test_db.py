import asyncio
import sys
sys.path.append('.')
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models import SiteModel
from sqlalchemy import select

async def test_db():
    async for db in get_db():
        try:
            # 测试简单查询
            stmt = select(SiteModel).limit(5)
            result = await db.execute(stmt)
            sites = result.scalars().all()
            print(f'找到 {len(sites)} 个站点')
            for site in sites:
                print(f'站点: {site.name} (ID: {site.id})')
        except Exception as e:
            print(f'数据库查询错误: {e}')
            import traceback
            traceback.print_exc()
        break

if __name__ == "__main__":
    asyncio.run(test_db()) 