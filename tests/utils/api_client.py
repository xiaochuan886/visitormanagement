"""
API客户端封装
提供统一的HTTP请求接口和认证管理
"""
import json
import time
from typing import Dict, Any, Optional, Union
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.access_token = None
        self.refresh_token = None
        self.tenant_id = "default"
        
        # 创建session并配置重试策略
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 请求日志
        self.request_logs = []
    
    def _log_request(self, method: str, url: str, request_data: Any, 
                    response_data: Any, status_code: int, duration: float):
        """记录请求日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "request_data": request_data,
            "response_data": response_data,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "success": 200 <= status_code < 300
        }
        self.request_logs.append(log_entry)
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        if self.tenant_id:
            headers["X-Tenant-ID"] = self.tenant_id
            
        return headers
    
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            params: 查询参数
            
        Returns:
            响应对象
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(
                    url, headers=headers, params=params, timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url, headers=headers, json=data, params=params, timeout=self.timeout
                )
            elif method.upper() == "PUT":
                response = self.session.put(
                    url, headers=headers, json=data, params=params, timeout=self.timeout
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(
                    url, headers=headers, params=params, timeout=self.timeout
                )
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            duration = time.time() - start_time
            
            # 尝试解析响应JSON
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # 记录请求日志
            self._log_request(
                method=method.upper(),
                url=url,
                request_data=data or params,
                response_data=response_data,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            self._log_request(
                method=method.upper(),
                url=url,
                request_data=data or params,
                response_data=str(e),
                status_code=0,
                duration=duration
            )
            raise
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录响应数据
        """
        login_data = {
            "username": username,
            "password": password
        }
        
        response = self._make_request("POST", "/api/v1/auth/login", data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            return data
        else:
            response.raise_for_status()
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        刷新访问令牌
        
        Returns:
            刷新响应数据
        """
        if not self.refresh_token:
            raise ValueError("没有可用的刷新令牌")
        
        refresh_data = {
            "refresh_token": self.refresh_token
        }
        
        response = self._make_request("POST", "/api/v1/auth/refresh", data=refresh_data)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            return data
        else:
            response.raise_for_status()
    
    def logout(self) -> Dict[str, Any]:
        """
        用户登出
        
        Returns:
            登出响应数据
        """
        response = self._make_request("POST", "/api/v1/auth/logout")
        
        if response.status_code == 200:
            self.access_token = None
            self.refresh_token = None
            return response.json()
        else:
            response.raise_for_status()
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            用户信息
        """
        response = self._make_request("GET", "/api/v1/auth/me")
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET请求"""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """POST请求"""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """PUT请求"""
        return self._make_request("PUT", endpoint, data=data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE请求"""
        return self._make_request("DELETE", endpoint)
    
    def set_tenant(self, tenant_id: str):
        """设置租户ID"""
        self.tenant_id = tenant_id
    
    def get_request_logs(self) -> list:
        """获取请求日志"""
        return self.request_logs
    
    def clear_logs(self):
        """清空请求日志"""
        self.request_logs.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取请求统计信息"""
        if not self.request_logs:
            return {}
        
        total_requests = len(self.request_logs)
        successful_requests = sum(1 for log in self.request_logs if log["success"])
        failed_requests = total_requests - successful_requests
        
        durations = [log["duration_ms"] for log in self.request_logs]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests * 100 if total_requests > 0 else 0,
            "avg_duration_ms": round(avg_duration, 2),
            "max_duration_ms": max_duration,
            "min_duration_ms": min_duration
        } 