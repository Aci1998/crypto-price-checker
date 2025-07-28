#!/usr/bin/env python3
"""
通用工具函数模块
提供各种常用的工具函数和装饰器
"""

import time
import hashlib
import secrets
import functools
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
import json
import re

logger = logging.getLogger(__name__)

# ==================== 时间工具 ====================

def get_current_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(datetime.now().timestamp())

def get_current_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）"""
    return int(datetime.now().timestamp() * 1000)

def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """时间戳转datetime对象"""
    if timestamp > 1e10:  # 毫秒时间戳
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp)

def datetime_to_timestamp(dt: datetime) -> int:
    """datetime对象转时间戳"""
    return int(dt.timestamp())

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化datetime对象"""
    return dt.strftime(format_str)

def parse_period_to_seconds(period: str) -> int:
    """解析时间周期字符串为秒数"""
    period = period.lower().strip()
    
    # 正则匹配数字和单位
    match = re.match(r'^(\d+)([smhd])$', period)
    if not match:
        raise ValueError(f"Invalid period format: {period}")
    
    value, unit = match.groups()
    value = int(value)
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    return value * multipliers[unit]

# ==================== 加密和安全工具 ====================

def generate_api_key(prefix: str = "ca_", length: int = 32) -> str:
    """生成API密钥"""
    random_part = secrets.token_urlsafe(length)
    return f"{prefix}{random_part}"

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """密码哈希"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # 使用PBKDF2进行密码哈希
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 迭代次数
    )
    
    return password_hash.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """验证密码"""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == password_hash

def generate_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    # 将所有参数序列化为字符串
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()

# ==================== 装饰器 ====================

def timing_decorator(func: Callable) -> Callable:
    """计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 毫秒
            logger.debug(f"{func.__name__} 执行时间: {execution_time:.2f}ms")
    
    return wrapper

def async_timing_decorator(func: Callable) -> Callable:
    """异步计时装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 毫秒
            logger.debug(f"{func.__name__} 执行时间: {execution_time:.2f}ms")
    
    return wrapper

def retry_decorator(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = delay * (backoff ** attempt)
                        logger.warning(f"{func.__name__} 第{attempt + 1}次尝试失败，{sleep_time}秒后重试: {e}")
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"{func.__name__} 所有重试都失败了")
            
            raise last_exception
        
        return wrapper
    return decorator

# ==================== 数据验证工具 ====================

def validate_symbol(symbol: str) -> bool:
    """验证货币代码格式"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    symbol = symbol.upper().strip()
    
    # 基本格式检查
    if not re.match(r'^[A-Z]{2,10}$', symbol):
        return False
    
    # 检查是否为交易对格式
    if '/' in symbol:
        parts = symbol.split('/')
        if len(parts) != 2:
            return False
        return all(re.match(r'^[A-Z]{2,10}$', part) for part in parts)
    
    return True

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_api_key(api_key: str, prefix: str = "ca_") -> bool:
    """验证API密钥格式"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    if not api_key.startswith(prefix):
        return False
    
    # 检查长度和字符
    key_part = api_key[len(prefix):]
    return len(key_part) >= 20 and re.match(r'^[A-Za-z0-9_-]+$', key_part)

# ==================== 数据转换工具 ====================

def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def normalize_symbol(symbol: str) -> str:
    """标准化货币代码"""
    if not symbol:
        return ""
    
    symbol = symbol.upper().strip()
    
    # 处理常见的分隔符
    symbol = symbol.replace('-', '/')
    
    return symbol

def format_price(price: float, precision: int = 2) -> str:
    """格式化价格显示"""
    if price >= 1:
        return f"${price:,.{precision}f}"
    else:
        # 对于小于1的价格，显示更多小数位
        return f"${price:.6f}".rstrip('0').rstrip('.')

def format_percentage(value: float, precision: int = 2) -> str:
    """格式化百分比显示"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{precision}f}%"

def format_volume(volume: float) -> str:
    """格式化交易量显示"""
    if volume >= 1e9:
        return f"{volume/1e9:.2f}B"
    elif volume >= 1e6:
        return f"{volume/1e6:.2f}M"
    elif volume >= 1e3:
        return f"{volume/1e3:.2f}K"
    else:
        return f"{volume:.2f}"

# ==================== 错误处理工具 ====================

class CryptoAgentError(Exception):
    """基础异常类"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()

class ValidationError(CryptoAgentError):
    """数据验证错误"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {
            'field': field,
            'value': value
        })

class APIError(CryptoAgentError):
    """API调用错误"""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message, "API_ERROR", {
            'status_code': status_code,
            'response': response
        })

class CacheError(CryptoAgentError):
    """缓存操作错误"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "CACHE_ERROR", {
            'operation': operation
        })

class DatabaseError(CryptoAgentError):
    """数据库操作错误"""
    def __init__(self, message: str, query: str = None):
        super().__init__(message, "DATABASE_ERROR", {
            'query': query
        })

# ==================== 导出 ====================

__all__ = [
    # 时间工具
    'get_current_timestamp',
    'get_current_timestamp_ms',
    'timestamp_to_datetime',
    'datetime_to_timestamp',
    'format_datetime',
    'parse_period_to_seconds',
    
    # 安全工具
    'generate_api_key',
    'hash_password',
    'verify_password',
    'generate_cache_key',
    
    # 装饰器
    'timing_decorator',
    'async_timing_decorator',
    'retry_decorator',
    
    # 验证工具
    'validate_symbol',
    'validate_email',
    'validate_api_key',
    
    # 转换工具
    'safe_float',
    'safe_int',
    'normalize_symbol',
    'format_price',
    'format_percentage',
    'format_volume',
    
    # 异常类
    'CryptoAgentError',
    'ValidationError',
    'APIError',
    'CacheError',
    'DatabaseError'
]