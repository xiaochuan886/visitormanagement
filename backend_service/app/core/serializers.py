"""
自定义序列化器
处理JSON序列化中的复杂类型
"""
import json
import decimal
from datetime import datetime, date, time
from typing import Any
from enum import Enum


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器"""
    
    def default(self, obj: Any) -> Any:
        """处理默认JSON编码器无法处理的类型"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, time):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, '__dict__'):
            # 处理自定义对象
            return obj.__dict__
        
        return super().default(obj)


def json_dumps(obj: Any, **kwargs) -> str:
    """自定义JSON序列化函数"""
    return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False, **kwargs)


def json_loads(s: str, **kwargs) -> Any:
    """自定义JSON反序列化函数"""
    return json.loads(s, **kwargs)


def serialize_for_cache(obj: Any) -> str:
    """为缓存序列化对象"""
    if hasattr(obj, 'dict'):
        # Pydantic模型
        data = obj.dict()
    elif hasattr(obj, '__dict__'):
        # 普通对象
        data = obj.__dict__
    else:
        # 基本类型
        data = obj
    
    return json_dumps(data)


def deserialize_from_cache(data: str, target_class=None) -> Any:
    """从缓存反序列化对象"""
    parsed_data = json_loads(data)
    
    if target_class and hasattr(target_class, 'parse_obj'):
        # Pydantic模型
        return target_class.parse_obj(parsed_data)
    
    return parsed_data 