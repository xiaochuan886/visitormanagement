#!/usr/bin/env python3
"""
简化启动脚本 - 不初始化数据库
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建简单的FastAPI应用
app = FastAPI(
    title="访客管理系统",
    description="简化版测试",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "访客管理系统 API",
        "status": "运行中",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 启动简化版访客管理系统...")
    uvicorn.run(
        "start_simple:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    ) 