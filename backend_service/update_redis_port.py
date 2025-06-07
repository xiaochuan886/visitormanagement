#!/usr/bin/env python3
"""
更新.env文件中的Redis端口配置
"""

if __name__ == "__main__":
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新Redis配置
        updated_content = content.replace(
            "REDIS_URL=redis://localhost:6379/0",
            "REDIS_URL=redis://localhost:6380/0"
        ).replace(
            "REDIS_PORT=6379",
            "REDIS_PORT=6380"
        ).replace(
            "CELERY_BROKER_URL=redis://localhost:6379/1",
            "CELERY_BROKER_URL=redis://localhost:6380/1"
        ).replace(
            "CELERY_RESULT_BACKEND=redis://localhost:6379/2",
            "CELERY_RESULT_BACKEND=redis://localhost:6380/2"
        )
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("✅ .env文件Redis端口配置已更新为6380")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}") 