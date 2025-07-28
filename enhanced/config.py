"""
增强版加密货币Agent配置管理
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """数据库配置"""
    # SQLite数据库路径
    MAIN_DB_PATH: str = os.getenv('DATABASE_PATH', 'data/crypto_agent.db')
    HISTORICAL_DB_PATH: str = os.getenv('HISTORICAL_DB_PATH', 'data/historical_data.db')
    USERS_DB_PATH: str = os.getenv('USERS_DB_PATH', 'data/users.db')
    
    # 数据库连接池配置
    MAX_CONNECTIONS: int = int(os.getenv('DB_MAX_CONNECTIONS', '20'))
    CONNECTION_TIMEOUT: int = int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))

@dataclass
class CacheConfig:
    """缓存配置"""
    # Redis配置
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_DB: int = int(os.getenv('REDIS_DB', '0'))
    
    # 缓存TTL配置（秒）
    DEFAULT_CACHE_TTL: int = int(os.getenv('DEFAULT_CACHE_TTL', '300'))  # 5分钟
    PRICE_CACHE_TTL: int = int(os.getenv('PRICE_CACHE_TTL', '60'))      # 1分钟
    TECHNICAL_CACHE_TTL: int = int(os.getenv('TECHNICAL_CACHE_TTL', '600'))  # 10分钟
    HISTORICAL_CACHE_TTL: int = int(os.getenv('HISTORICAL_CACHE_TTL', '3600'))  # 1小时
    
    # 内存缓存配置
    MEMORY_CACHE_SIZE: int = int(os.getenv('MEMORY_CACHE_SIZE', '1000'))
    MEMORY_CACHE_TTL: int = int(os.getenv('MEMORY_CACHE_TTL', '300'))

@dataclass
class APIConfig:
    """API配置"""
    # 服务器配置
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '5000'))
    DEBUG: bool = os.getenv('FLASK_ENV', 'production') == 'development'
    
    # API限制
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv('MAX_CONCURRENT_REQUESTS', '100'))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    MAX_BATCH_SIZE: int = int(os.getenv('MAX_BATCH_SIZE', '10'))
    
    # 外部API配置
    EXTERNAL_API_TIMEOUT: int = int(os.getenv('EXTERNAL_API_TIMEOUT', '15'))
    EXTERNAL_API_RETRIES: int = int(os.getenv('EXTERNAL_API_RETRIES', '3'))

@dataclass
class SecurityConfig:
    """安全配置"""
    # JWT配置
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # API密钥配置
    API_KEY_PREFIX: str = os.getenv('API_KEY_PREFIX', 'ca_')
    API_KEY_LENGTH: int = int(os.getenv('API_KEY_LENGTH', '32'))
    
    # 限流配置
    DEFAULT_DAILY_QUOTA: int = int(os.getenv('DEFAULT_DAILY_QUOTA', '1000'))
    PREMIUM_DAILY_QUOTA: int = int(os.getenv('PREMIUM_DAILY_QUOTA', '10000'))
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))

@dataclass
class TechnicalAnalysisConfig:
    """技术分析配置"""
    # 历史数据配置
    MAX_HISTORICAL_DAYS: int = int(os.getenv('MAX_HISTORICAL_DAYS', '90'))
    DEFAULT_HISTORICAL_DAYS: int = int(os.getenv('DEFAULT_HISTORICAL_DAYS', '30'))
    
    # 技术指标配置
    RSI_PERIOD: int = int(os.getenv('RSI_PERIOD', '14'))
    MACD_FAST_PERIOD: int = int(os.getenv('MACD_FAST_PERIOD', '12'))
    MACD_SLOW_PERIOD: int = int(os.getenv('MACD_SLOW_PERIOD', '26'))
    MACD_SIGNAL_PERIOD: int = int(os.getenv('MACD_SIGNAL_PERIOD', '9'))
    BOLLINGER_PERIOD: int = int(os.getenv('BOLLINGER_PERIOD', '20'))
    BOLLINGER_STD: float = float(os.getenv('BOLLINGER_STD', '2.0'))
    
    # 支持的时间间隔
    DEFAULT_INTERVAL: str = os.getenv('DEFAULT_INTERVAL', '1h')
    
    def get_supported_intervals(self) -> list:
        """获取支持的时间间隔"""
        return ['1m', '5m', '15m', '1h', '4h', '1d', '1w']

@dataclass
class LoggingConfig:
    """日志配置"""
    # 日志级别
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # 日志文件配置
    LOG_FILE_PATH: str = os.getenv('LOG_FILE_PATH', 'logs/crypto_agent.log')
    LOG_MAX_SIZE: int = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # 日志格式
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@dataclass
class MonitoringConfig:
    """监控配置"""
    # 健康检查
    HEALTH_CHECK_INTERVAL: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))
    
    # 性能监控
    ENABLE_METRICS: bool = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT: int = int(os.getenv('METRICS_PORT', '9090'))
    
    # 告警配置
    ALERT_EMAIL: Optional[str] = os.getenv('ALERT_EMAIL')
    ALERT_WEBHOOK: Optional[str] = os.getenv('ALERT_WEBHOOK')

class Config:
    """主配置类"""
    
    def __init__(self):
        # 环境配置
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = self.environment == 'development'
        
        # 各模块配置
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        self.technical_analysis = TechnicalAnalysisConfig()
        self.logging = LoggingConfig()
        self.monitoring = MonitoringConfig()
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        import os
        
        directories = [
            'data',
            'logs',
            'cache',
            'backups'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def validate(self) -> list:
        """验证配置的有效性"""
        errors = []
        
        # 验证必要的配置项
        if not self.security.JWT_SECRET or self.security.JWT_SECRET == 'your-secret-key-change-in-production':
            if self.is_production():
                errors.append("生产环境必须设置JWT_SECRET")
        
        # 验证数据库路径
        for db_path in [self.database.MAIN_DB_PATH, self.database.HISTORICAL_DB_PATH, self.database.USERS_DB_PATH]:
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建数据库目录 {db_dir}: {e}")
        
        # 验证端口配置
        if not (1024 <= self.api.PORT <= 65535):
            errors.append(f"API端口 {self.api.PORT} 不在有效范围内 (1024-65535)")
        
        return errors
    
    def get_database_url(self, db_type: str = 'main') -> str:
        """获取数据库URL"""
        db_paths = {
            'main': self.database.MAIN_DB_PATH,
            'historical': self.database.HISTORICAL_DB_PATH,
            'users': self.database.USERS_DB_PATH
        }
        
        if db_type not in db_paths:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        return f"sqlite:///{db_paths[db_type]}"
    
    def is_production(self) -> bool:
        """判断是否为生产环境"""
        return not self.api.DEBUG
    
    def get_supported_indicators(self) -> list:
        """获取支持的技术指标列表"""
        return [
            'rsi',
            'macd',
            'bollinger_bands',
            'sma',
            'ema',
            'stochastic',
            'williams_r',
            'cci'
        ]

# 全局配置实例
config = Config()

# 验证配置
config_errors = config.validate()
if config_errors:
    print("配置验证失败:")
    for error in config_errors:
        print(f"  - {error}")
    if config.is_production():
        raise RuntimeError("生产环境配置验证失败")

# 导出常用配置
__all__ = [
    'config',
    'DatabaseConfig',
    'CacheConfig', 
    'APIConfig',
    'SecurityConfig',
    'TechnicalAnalysisConfig',
    'LoggingConfig',
    'MonitoringConfig'
]