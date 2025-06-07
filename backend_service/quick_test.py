#!/usr/bin/env python3
"""
快速API测试脚本 - 诊断问题
"""

import requests
import json
import sys

def test_basic_connection():
    """测试基础连接"""
    try:
        print("🔍 测试基础连接...")
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ 根路径响应: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_health_check():
    """测试健康检查"""
    try:
        print("🔍 测试健康检查...")
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"✅ 健康检查响应: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_auth_login():
    """测试登录"""
    try:
        print("🔍 测试用户登录...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/login", 
            json=login_data,
            timeout=10
        )
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ 登录成功，获取到令牌")
                return data["access_token"]
            else:
                print(f"❌ 登录响应格式错误: {data}")
        else:
            print(f"❌ 登录失败: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_sites_api(token):
    """测试站点API"""
    if not token:
        print("❌ 没有有效令牌，跳过站点测试")
        return
    
    try:
        print("🔍 测试站点API...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取站点列表
        response = requests.get(
            "http://127.0.0.1:8000/api/v1/sites/",
            headers=headers,
            timeout=10
        )
        print(f"获取站点列表响应: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 站点列表获取成功，共 {data.get('total', 0)} 个站点")
        else:
            print(f"❌ 获取站点列表失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 站点API测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始快速API测试...")
    
    # 测试基础连接
    if not test_basic_connection():
        print("❌ 基础连接失败，退出测试")
        sys.exit(1)
    
    # 测试健康检查
    test_health_check()
    
    # 测试登录
    token = test_auth_login()
    
    # 测试站点API
    test_sites_api(token)
    
    print("🎉 快速测试完成")

if __name__ == "__main__":
    main() 