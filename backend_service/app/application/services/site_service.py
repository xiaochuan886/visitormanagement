"""
站点服务层
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import SiteModel
from app.application.dto.site_dto import (
    SiteCreateDTO,
    SiteUpdateDTO,
    SiteResponseDTO,
    SiteListResponseDTO,
    SiteQueryDTO
)
from app.domain.base_enums import SiteStatus
from app.infrastructure.cache.redis_client import get_redis
from app.core.config import settings


class SiteService:
    """站点服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_site(
        self, 
        site_data: SiteCreateDTO, 
        created_by: str, 
        tenant_id: str
    ) -> SiteResponseDTO:
        """创建站点"""
        # 检查站点编码是否已存在
        existing_site = await self._get_site_by_code(site_data.code, tenant_id)
        if existing_site:
            raise ValueError(f"站点编码 {site_data.code} 已存在")
        
        # 创建站点模型
        site = SiteModel(
            name=site_data.name,
            code=site_data.code,
            address=site_data.address,
            city=site_data.city,
            province=site_data.province,
            postal_code=site_data.postal_code,
            phone=site_data.phone_number,  # 字段名映射
            email=site_data.email,
            description=site_data.description,
            working_hours_start=str(site_data.working_hours_start) if site_data.working_hours_start else None,
            working_hours_end=str(site_data.working_hours_end) if site_data.working_hours_end else None,
            timezone=site_data.timezone,
            status=site_data.status.value if site_data.status else "active",
            tenant_id=tenant_id,
            created_by=created_by
        )
        
        self.db.add(site)
        await self.db.commit()
        await self.db.refresh(site)
        
        # 缓存站点信息 (暂时禁用)
        await self._cache_site(site)
        
        return SiteResponseDTO.from_orm(site)
    
    async def get_sites(
        self, 
        query: SiteQueryDTO, 
        tenant_id: str
    ) -> SiteListResponseDTO:
        """获取站点列表"""
        # 构建查询条件
        conditions = [SiteModel.tenant_id == tenant_id, SiteModel.is_deleted == False]
        
        if query.name:
            conditions.append(SiteModel.name.ilike(f"%{query.name}%"))
        if query.code:
            conditions.append(SiteModel.code.ilike(f"%{query.code}%"))
        if query.city:
            conditions.append(SiteModel.city.ilike(f"%{query.city}%"))
        if query.province:
            conditions.append(SiteModel.province.ilike(f"%{query.province}%"))
        if query.status:
            conditions.append(SiteModel.status == query.status)
        
        # 查询总数
        count_stmt = select(func.count(SiteModel.id)).where(and_(*conditions))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar()
        
        # 分页查询
        offset = (query.page - 1) * query.page_size
        stmt = (
            select(SiteModel)
            .where(and_(*conditions))
            .offset(offset)
            .limit(query.page_size)
            .order_by(SiteModel.created_at.desc())
        )
        
        result = await self.db.execute(stmt)
        sites = result.scalars().all()
        
        # 计算总页数
        total_pages = (total + query.page_size - 1) // query.page_size
        
        return SiteListResponseDTO(
            items=[SiteResponseDTO.from_orm(site) for site in sites],
            total=total,
            page=query.page,
            page_size=query.page_size,
            total_pages=total_pages
        )
    
    async def get_site_by_id(
        self, 
        site_id: int, 
        tenant_id: str
    ) -> Optional[SiteResponseDTO]:
        """根据ID获取站点"""
        # 先尝试从缓存获取 (暂时禁用)
        cached_site = await self._get_cached_site(site_id, tenant_id)
        if cached_site:
            return cached_site
        
        # 从数据库查询
        stmt = (
            select(SiteModel)
            .where(
                and_(
                    SiteModel.id == site_id,
                    SiteModel.tenant_id == tenant_id,
                    SiteModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        site = result.scalar_one_or_none()
        
        if site:
            # 缓存站点信息 (暂时禁用)
            await self._cache_site(site)
            return SiteResponseDTO.from_orm(site)
        
        return None
    
    async def update_site(
        self, 
        site_id: int, 
        site_data: SiteUpdateDTO, 
        updated_by: str, 
        tenant_id: str
    ) -> Optional[SiteResponseDTO]:
        """更新站点信息"""
        # 获取站点
        stmt = (
            select(SiteModel)
            .where(
                and_(
                    SiteModel.id == site_id,
                    SiteModel.tenant_id == tenant_id,
                    SiteModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        site = result.scalar_one_or_none()
        
        if not site:
            return None
        
        # 如果更新编码，检查是否重复
        if site_data.code and site_data.code != site.code:
            existing_site = await self._get_site_by_code(site_data.code, tenant_id)
            if existing_site and existing_site.id != site_id:
                raise ValueError(f"站点编码 {site_data.code} 已存在")
        
        # 更新字段
        update_data = site_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(site, field, value)
        
        site.updated_by = updated_by
        site.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(site)
        
        # 更新缓存 (暂时禁用)
        await self._cache_site(site)
        
        return SiteResponseDTO.from_orm(site)
    
    async def delete_site(
        self, 
        site_id: int, 
        deleted_by: str, 
        tenant_id: str
    ) -> bool:
        """删除站点（软删除）"""
        # 获取站点
        stmt = (
            select(SiteModel)
            .where(
                and_(
                    SiteModel.id == site_id,
                    SiteModel.tenant_id == tenant_id,
                    SiteModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        site = result.scalar_one_or_none()
        
        if not site:
            return False
        
        # 软删除
        site.is_deleted = True
        site.deleted_by = deleted_by
        site.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        
        # 清除缓存 (暂时禁用)
        await self._clear_site_cache(site_id, tenant_id)
        
        return True
    
    async def _get_site_by_code(
        self, 
        code: str, 
        tenant_id: str
    ) -> Optional[SiteModel]:
        """根据编码获取站点"""
        stmt = (
            select(SiteModel)
            .where(
                and_(
                    SiteModel.code == code,
                    SiteModel.tenant_id == tenant_id,
                    SiteModel.is_deleted == False
                )
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _cache_site(self, site: SiteModel) -> None:
        """缓存站点信息"""
        try:
            redis = await get_redis()
            cache_key = f"site:{site.tenant_id}:{site.id}"
            site_data = SiteResponseDTO.from_orm(site).dict()
            await redis.setex(cache_key, 3600, str(site_data))  # 缓存1小时
        except Exception as e:
            # 缓存失败不影响主流程
            print(f"缓存站点信息失败: {e}")
    
    async def _get_cached_site(
        self, 
        site_id: int, 
        tenant_id: str
    ) -> Optional[SiteResponseDTO]:
        """从缓存获取站点信息"""
        try:
            redis = await get_redis()
            cache_key = f"site:{tenant_id}:{site_id}"
            cached_data = await redis.get(cache_key)
            if cached_data:
                site_dict = eval(cached_data)  # 注意：生产环境应使用json.loads
                return SiteResponseDTO(**site_dict)
        except Exception as e:
            # 缓存读取失败不影响主流程
            print(f"读取站点缓存失败: {e}")
        
        return None
    
    async def _clear_site_cache(self, site_id: int, tenant_id: str) -> None:
        """清除站点缓存"""
        try:
            redis = await get_redis()
            cache_key = f"site:{tenant_id}:{site_id}"
            await redis.delete(cache_key)
        except Exception as e:
            # 缓存清除失败不影响主流程
            print(f"清除站点缓存失败: {e}") 