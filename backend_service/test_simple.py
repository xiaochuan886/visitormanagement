#!/usr/bin/env python3
"""
最简单的测试应用
"""

import uvicorn
from fastapi import FastAPI

# 创建简单的FastAPI应用
app = FastAPI(
    title="访客管理系统测试",
    description="简化版测试",
    version="1.0.0"
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
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    ) 