#!/usr/bin/env python3
"""
更新.env文件中的数据库端口配置
"""

if __name__ == "__main__":
    # 读取当前.env文件
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新数据库配置
        updated_content = content.replace(
            "DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5432/visitor_management",
            "DATABASE_URL=postgresql+asyncpg://postgres:password123@localhost:5433/visitor_management"
        ).replace(
            "DATABASE_PORT=5432",
            "DATABASE_PORT=5433"
        )
        
        # 写回文件
        with open(".env", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("✅ .env文件端口配置已更新为5433")
        
    except FileNotFoundError:
        print("❌ .env文件不存在，请先创建.env文件")
    except Exception as e:
        print(f"❌ 更新失败: {e}") 