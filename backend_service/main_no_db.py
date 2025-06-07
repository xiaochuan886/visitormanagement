"""
访客管理系统 - FastAPI应用入口 (不初始化数据库版本)
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import api_router
from app.api.middleware.exception_handler import exception_handler_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 不初始化数据库"""
    # 启动时执行
    setup_logging()
    print("🚀 启动访客管理系统 (测试模式)...")
    print("⚠️  跳过数据库初始化")
    
    yield
    
    # 关闭时执行
    print("🛑 访客管理系统关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title=settings.app_name,
        description="基于FastAPI的现代化访客管理系统 (测试模式)",
        version=settings.app_version,
        debug=True,  # 强制开启调试模式
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加全局异常处理中间件
    app.middleware("http")(exception_handler_middleware)
    
    # 注册API路由
    app.include_router(api_router, prefix="/api/v1")
    
    # 配置静态文件服务
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    except Exception:
        # 开发环境中目录可能不存在
        pass
    
    @app.get("/")
    async def root():
        """根路径健康检查"""
        return {
            "message": f"欢迎使用{settings.app_name} (测试模式)",
            "version": settings.app_version,
            "status": "运行中",
            "mode": "测试模式 - 未连接数据库"
        }
    
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy", 
            "version": settings.app_version,
            "mode": "test"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main_no_db:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info",
    ) 