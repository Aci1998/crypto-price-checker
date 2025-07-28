#!/usr/bin/env python3
"""
数据库管理模块
提供统一的数据库连接、初始化和迁移功能
"""

import sqlite3
import os
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime

from .config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_configs = {
            'main': config.database.main_db_path,
            'historical': config.database.historical_db_path,
            'users': config.database.users_db_path
        }
        
        # 确保数据库目录存在
        for db_path in self.db_configs.values():
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化所有数据库
        self.initialize_databases()
    
    @contextmanager
    def get_connection(self, db_type: str = 'main'):
        """获取数据库连接的上下文管理器"""
        if db_type not in self.db_configs:
            raise ValueError(f"Unknown database type: {db_type}")
        
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_configs[db_type],
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row  # 启用字典式访问
            conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
            conn.execute("PRAGMA journal_mode = WAL")  # 启用WAL模式提高并发性能
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error for {db_type}: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def initialize_databases(self):
        """初始化所有数据库表结构"""
        logger.info("初始化数据库表结构...")
        
        # 初始化主数据库
        self._init_main_database()
        
        # 初始化历史数据数据库
        self._init_historical_database()
        
        # 初始化用户数据库
        self._init_users_database()
        
        logger.info("数据库初始化完成")
    
    def _init_main_database(self):
        """初始化主数据库"""
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            
            # 系统配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    description TEXT,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
            ''')
            
            # 支持的加密货币表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS supported_currencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    supports_technical_analysis BOOLEAN DEFAULT 1,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
            ''')
            
            # 数据源配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    base_url TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    priority INTEGER DEFAULT 1,
                    rate_limit_per_minute INTEGER DEFAULT 60,
                    timeout_seconds INTEGER DEFAULT 30,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_currencies_symbol ON supported_currencies(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_sources_priority ON data_sources(priority, is_active)')
            
            # 插入初始数据
            self._insert_initial_main_data(cursor)
            
            conn.commit()
    
    def _init_historical_database(self):
        """初始化历史数据数据库"""
        with self.get_connection('historical') as conn:
            cursor = conn.cursor()
            
            # 价格历史数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume REAL NOT NULL,
                    interval_type TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    UNIQUE(symbol, timestamp, interval_type, data_source)
                )
            ''')
            
            # 技术指标缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS technical_indicators_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    indicator_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    calculated_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    UNIQUE(symbol, indicator_type, parameters)
                )
            ''')
            
            # 数据同步状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    interval_type TEXT NOT NULL,
                    last_sync_timestamp INTEGER NOT NULL,
                    last_sync_at INTEGER NOT NULL,
                    sync_status TEXT DEFAULT 'success',
                    error_message TEXT,
                    UNIQUE(symbol, data_source, interval_type)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_symbol_time ON price_history(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_interval ON price_history(interval_type, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_cache_symbol ON technical_indicators_cache(symbol, expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status_symbol ON sync_status(symbol, data_source)')
            
            conn.commit()
    
    def _init_users_database(self):
        """初始化用户数据库"""
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    daily_quota INTEGER DEFAULT 1000,
                    is_active BOOLEAN DEFAULT 1,
                    is_premium BOOLEAN DEFAULT 0,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    last_login_at INTEGER
                )
            ''')
            
            # API使用记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    api_key TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    request_size INTEGER DEFAULT 0,
                    response_size INTEGER DEFAULT 0,
                    response_time_ms INTEGER NOT NULL,
                    status_code INTEGER NOT NULL,
                    error_message TEXT,
                    timestamp INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 用户配额使用统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quota_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    requests_count INTEGER DEFAULT 0,
                    quota_limit INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_user_time ON api_usage(user_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_quota_usage_user_date ON quota_usage(user_id, date)')
            
            conn.commit()
    
    def _insert_initial_main_data(self, cursor):
        """插入初始主数据"""
        current_time = int(datetime.now().timestamp())
        
        # 插入系统配置
        system_configs = [
            ('version', '1.1.0', '系统版本'),
            ('initialized_at', str(current_time), '系统初始化时间'),
            ('default_cache_ttl', '300', '默认缓存TTL（秒）'),
            ('max_historical_days', '90', '最大历史数据天数'),
            ('enable_technical_analysis', '1', '启用技术分析功能')
        ]
        
        for key, value, description in system_configs:
            cursor.execute('''
                INSERT OR IGNORE INTO system_config (key, value, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, value, description, current_time, current_time))
        
        # 插入支持的加密货币
        currencies = [
            ('BTC', 'Bitcoin', 1, 1),
            ('ETH', 'Ethereum', 1, 1),
            ('ADA', 'Cardano', 1, 1),
            ('DOT', 'Polkadot', 1, 1),
            ('LINK', 'Chainlink', 1, 1),
            ('LTC', 'Litecoin', 1, 1),
            ('XRP', 'Ripple', 1, 1),
            ('BNB', 'Binance Coin', 1, 1),
            ('SOL', 'Solana', 1, 1),
            ('MATIC', 'Polygon', 1, 1),
            ('AVAX', 'Avalanche', 1, 1),
            ('DOGE', 'Dogecoin', 1, 1),
            ('SHIB', 'Shiba Inu', 1, 1),
            ('UNI', 'Uniswap', 1, 1),
            ('ATOM', 'Cosmos', 1, 1)
        ]
        
        for symbol, name, is_active, supports_ta in currencies:
            cursor.execute('''
                INSERT OR IGNORE INTO supported_currencies 
                (symbol, name, is_active, supports_technical_analysis, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, name, is_active, supports_ta, current_time, current_time))
        
        # 插入数据源配置
        data_sources = [
            ('OKX', 'https://www.okx.com/api/v5', 1, 1, 60, 30),
            ('Binance', 'https://api.binance.com/api/v3', 1, 2, 60, 30),
            ('CoinGecko', 'https://api.coingecko.com/api/v3', 1, 3, 30, 30)
        ]
        
        for name, base_url, is_active, priority, rate_limit, timeout in data_sources:
            cursor.execute('''
                INSERT OR IGNORE INTO data_sources 
                (name, base_url, is_active, priority, rate_limit_per_minute, timeout_seconds, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, base_url, is_active, priority, rate_limit, timeout, current_time, current_time))
    
    def get_supported_currencies(self) -> List[Dict[str, Any]]:
        """获取支持的加密货币列表"""
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT symbol, name, supports_technical_analysis
                FROM supported_currencies
                WHERE is_active = 1
                ORDER BY symbol
            ''')
            
            return [
                {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'supports_technical_analysis': bool(row['supports_technical_analysis'])
                }
                for row in cursor.fetchall()
            ]
    
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """获取数据源配置"""
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, base_url, priority, rate_limit_per_minute, timeout_seconds
                FROM data_sources
                WHERE is_active = 1
                ORDER BY priority
            ''')
            
            return [
                {
                    'name': row['name'],
                    'base_url': row['base_url'],
                    'priority': row['priority'],
                    'rate_limit_per_minute': row['rate_limit_per_minute'],
                    'timeout_seconds': row['timeout_seconds']
                }
                for row in cursor.fetchall()
            ]
    
    def get_system_config(self, key: str, default: Any = None) -> Any:
        """获取系统配置"""
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM system_config WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
    
    def set_system_config(self, key: str, value: str, description: str = None):
        """设置系统配置"""
        current_time = int(datetime.now().timestamp())
        
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_config (key, value, description, created_at, updated_at)
                VALUES (?, ?, ?, 
                    COALESCE((SELECT created_at FROM system_config WHERE key = ?), ?),
                    ?)
            ''', (key, value, description, key, current_time, current_time))
            conn.commit()
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cutoff_time = int((datetime.now().timestamp() - (days * 24 * 3600)))
        
        with self.get_connection('historical') as conn:
            cursor = conn.cursor()
            
            # 清理旧的价格历史数据
            cursor.execute('DELETE FROM price_history WHERE timestamp < ?', (cutoff_time,))
            deleted_price_records = cursor.rowcount
            
            # 清理过期的技术指标缓存
            cursor.execute('DELETE FROM technical_indicators_cache WHERE expires_at < ?', (int(datetime.now().timestamp()),))
            deleted_cache_records = cursor.rowcount
            
            conn.commit()
        
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            
            # 清理旧的API使用记录（保留最近30天）
            api_cutoff_time = int((datetime.now().timestamp() - (30 * 24 * 3600)))
            cursor.execute('DELETE FROM api_usage WHERE timestamp < ?', (api_cutoff_time,))
            deleted_api_records = cursor.rowcount
            
            conn.commit()
        
        logger.info(f"数据清理完成: 价格记录 {deleted_price_records}, 缓存记录 {deleted_cache_records}, API记录 {deleted_api_records}")
        
        return {
            'price_records_deleted': deleted_price_records,
            'cache_records_deleted': deleted_cache_records,
            'api_records_deleted': deleted_api_records
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        # 主数据库统计
        with self.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM supported_currencies WHERE is_active = 1')
            stats['active_currencies'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM data_sources WHERE is_active = 1')
            stats['active_data_sources'] = cursor.fetchone()['count']
        
        # 历史数据库统计
        with self.get_connection('historical') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM price_history')
            stats['price_history_records'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM technical_indicators_cache WHERE expires_at > ?', (int(datetime.now().timestamp()),))
            stats['active_cache_records'] = cursor.fetchone()['count']
        
        # 用户数据库统计
        with self.get_connection('users') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE is_active = 1')
            stats['active_users'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM api_usage WHERE timestamp > ?', (int((datetime.now().timestamp() - 24*3600)),))
            stats['api_requests_24h'] = cursor.fetchone()['count']
        
        return stats

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 导出
__all__ = ['DatabaseManager', 'db_manager']