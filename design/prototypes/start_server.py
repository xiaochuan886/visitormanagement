#!/usr/bin/env python3
"""
访客管理系统 UI 原型预览服务器

使用方法:
    python start_server.py [端口号]

默认端口: 8000
"""

import http.server
import socketserver
import webbrowser
import sys
import os
from pathlib import Path

def main():
    # 默认端口
    port = 8000
    
    # 如果提供了端口参数
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("错误: 端口号必须是数字")
            sys.exit(1)
    
    # 确保在正确的目录中
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 检查index.html是否存在
    if not Path("index.html").exists():
        print("错误: 找不到 index.html 文件")
        print("请确保在 design/prototypes 目录中运行此脚本")
        sys.exit(1)
    
    # 创建HTTP服务器
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 访客管理系统 UI 原型服务器启动成功!")
            print(f"📍 服务地址: http://localhost:{port}")
            print(f"📁 服务目录: {script_dir}")
            print(f"🌐 正在自动打开浏览器...")
            print(f"⏹️  按 Ctrl+C 停止服务器")
            print("-" * 50)
            
            # 自动打开浏览器
            webbrowser.open(f"http://localhost:{port}")
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 错误: 端口 {port} 已被占用")
            print(f"💡 请尝试使用其他端口: python start_server.py {port + 1}")
        else:
            print(f"❌ 启动服务器时出错: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        print("👋 感谢使用访客管理系统 UI 原型!")

if __name__ == "__main__":
    main() 