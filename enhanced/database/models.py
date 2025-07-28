"""
数据库模型定义

定义所有数据库表的结构和关系
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class PriceHistory(Base):
    """价格历史数据表"""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(Integer, nullable=False, index=True)  # Unix时间戳
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    interval_type = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d等
    data_source = Column(String(20), nullable=False)    # OKX, Binance, CoinGecko
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 复合索引
    __table_args__ = (
        Index('idx_symbol_timestamp_interval', 'symbol', 'timestamp', 'interval_type'),
        Index('idx_symbol_interval_timestamp', 'symbol', 'interval_type', 'timestamp'),
    )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timestamp': self.timestamp,
            'open': self.open_price,
            'high': self.high_price,
            'low': self.low_price,
            'close': self.close_price,
            'volume': self.volume,
            'interval': self.interval_type,
            'source': self.data_source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<PriceHistory(symbol='{self.symbol}', timestamp={self.timestamp}, close={self.close_price})>"

class User(Base):
    """用户表"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    
    # 配额和权限
    daily_quota = Column(Integer, default=1000, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    last_api_call = Column(DateTime)
    
    # 用户设置（JSON格式存储）
    settings = Column(Text)  # JSON字符串
    
    # 关系
    api_usage_records = relationship("APIUsage", back_populates="user", cascade="all, delete-orphan")
    
    def get_settings(self):
        """获取用户设置"""
        if self.settings:
            try:
                return json.loads(self.settings)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_settings(self, settings_dict):
        """设置用户设置"""
        self.settings = json.dumps(settings_dict)
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'daily_quota': self.daily_quota,
            'is_premium': self.is_premium,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'settings': self.get_settings()
        }
        
        if include_sensitive:
            data['api_key'] = self.api_key
        
        return data
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', active={self.is_active})>"

class APIUsage(Base):
    """API使用记录表"""
    __tablename__ = 'api_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    api_key = Column(String(64), nullable=False, index=True)
    
    # 请求信息
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False, default='GET')
    query_params = Column(Text)  # JSON字符串存储查询参数
    
    # 响应信息
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    response_size_bytes = Column(Integer)
    
    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # IP和用户代理
    ip_address = Column(String(45))  # 支持IPv6
    user_agent = Column(String(500))
    
    # 错误信息（如果有）
    error_message = Column(Text)
    
    # 关系
    user = relationship("User", back_populates="api_usage_records")
    
    # 索引
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_api_key_timestamp', 'api_key', 'timestamp'),
        Index('idx_endpoint_timestamp', 'endpoint', 'timestamp'),
    )
    
    def get_query_params(self):
        """获取查询参数"""
        if self.query_params:
            try:
                return json.loads(self.query_params)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_query_params(self, params_dict):
        """设置查询参数"""
        self.query_params = json.dumps(params_dict)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'api_key': self.api_key,
            'endpoint': self.endpoint,
            'method': self.method,
            'query_params': self.get_query_params(),
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'response_size_bytes': self.response_size_bytes,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f"<APIUsage(user_id={self.user_id}, endpoint='{self.endpoint}', status={self.status_code})>"

class TechnicalIndicatorCache(Base):
    """技术指标缓存表"""
    __tablename__ = 'technical_indicator_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False)  # rsi, macd, bollinger_bands等
    interval_type = Column(String(10), nullable=False)   # 1h, 1d等
    parameters = Column(Text)  # JSON格式存储指标参数
    
    # 计算结果
    result_data = Column(Text, nullable=False)  # JSON格式存储计算结果
    
    # 时间戳
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # 复合索引
    __table_args__ = (
        Index('idx_symbol_indicator_interval', 'symbol', 'indicator_type', 'interval_type'),
        Index('idx_expires_at', 'expires_at'),
    )
    
    def get_parameters(self):
        """获取指标参数"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_parameters(self, params_dict):
        """设置指标参数"""
        self.parameters = json.dumps(params_dict)
    
    def get_result_data(self):
        """获取计算结果"""
        if self.result_data:
            try:
                return json.loads(self.result_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_result_data(self, result_dict):
        """设置计算结果"""
        self.result_data = json.dumps(result_dict)
    
    def is_expired(self):
        """检查是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'indicator_type': self.indicator_type,
            'interval_type': self.interval_type,
            'parameters': self.get_parameters(),
            'result_data': self.get_result_data(),
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired()
        }
    
    def __repr__(self):
        return f"<TechnicalIndicatorCache(symbol='{self.symbol}', indicator='{self.indicator_type}')>"

# 为了向后兼容，保留原有的简单模型
class LegacyCryptoData(Base):
    """遗留的加密货币数据表（向后兼容）"""
    __tablename__ = 'legacy_crypto_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    change_24h = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LegacyCryptoData(symbol='{self.symbol}', price={self.price})>"