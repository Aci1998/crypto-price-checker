#!/usr/bin/env python3
"""
数据库迁移管理模块
处理数据库版本升级和数据迁移
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Migration:
    """单个迁移类"""
    
    def __init__(self, version: str, description: str, up_func: Callable, down_func: Callable = None):
        self.version = version
        self.description = description
        self.up_func = up_func
        self.down_func = down_func
        self.timestamp = datetime.now()
    
    def apply(self, conn: sqlite3.Connection):
        """应用迁移"""
        logger.info(f"应用迁移 {self.version}: {self.description}")
        self.up_func(conn)
    
    def rollback(self, conn: sqlite3.Connection):
        """回滚迁移"""
        if self.down_func:
            logger.info(f"回滚迁移 {self.version}: {self.description}")
            self.down_func(conn)
        else:
            logger.warning(f"迁移 {self.version} 没有回滚函数")

class MigrationManager:
    """迁移管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations: List[Migration] = []
        self._ensure_migration_table()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库连接错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _ensure_migration_table(self):
        """确保迁移表存在"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    applied_at INTEGER NOT NULL
                )
            ''')
            conn.commit()
    
    def add_migration(self, migration: Migration):
        """添加迁移"""
        self.migrations.append(migration)
        # 按版本号排序
        self.migrations.sort(key=lambda m: m.version)
    
    def get_applied_migrations(self) -> List[str]:
        """获取已应用的迁移版本列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT version FROM schema_migrations ORDER BY version')
            return [row['version'] for row in cursor.fetchall()]
    
    def get_pending_migrations(self) -> List[Migration]:
        """获取待应用的迁移"""
        applied_versions = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied_versions]
    
    def apply_migrations(self):
        """应用所有待处理的迁移"""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("没有待应用的迁移")
            return
        
        logger.info(f"发现 {len(pending)} 个待应用的迁移")
        
        with self.get_connection() as conn:
            for migration in pending:
                try:
                    # 应用迁移
                    migration.apply(conn)
                    
                    # 记录迁移
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO schema_migrations (version, description, applied_at)
                        VALUES (?, ?, ?)
                    ''', (migration.version, migration.description, int(datetime.now().timestamp())))
                    
                    conn.commit()
                    logger.info(f"迁移 {migration.version} 应用成功")
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"迁移 {migration.version} 应用失败: {e}")
                    raise
    
    def rollback_migration(self, version: str):
        """回滚指定版本的迁移"""
        migration = next((m for m in self.migrations if m.version == version), None)
        if not migration:
            raise ValueError(f"未找到版本 {version} 的迁移")
        
        applied_versions = self.get_applied_migrations()
        if version not in applied_versions:
            logger.warning(f"迁移 {version} 尚未应用，无需回滚")
            return
        
        with self.get_connection() as conn:
            try:
                # 回滚迁移
                migration.rollback(conn)
                
                # 删除迁移记录
                cursor = conn.cursor()
                cursor.execute('DELETE FROM schema_migrations WHERE version = ?', (version,))
                
                conn.commit()
                logger.info(f"迁移 {version} 回滚成功")
                
            except Exception as e:
                conn.rollback()
                logger.error(f"迁移 {version} 回滚失败: {e}")
                raise
    
    def get_migration_status(self) -> Dict[str, Any]:
        """获取迁移状态"""
        applied = self.get_applied_migrations()
        pending = self.get_pending_migrations()
        
        return {
            'total_migrations': len(self.migrations),
            'applied_count': len(applied),
            'pending_count': len(pending),
            'applied_versions': applied,
            'pending_versions': [m.version for m in pending],
            'last_applied': applied[-1] if applied else None
        }

# ==================== 具体的迁移定义 ====================

def create_initial_schema_main(conn: sqlite3.Connection):
    """创建主数据库初始架构"""
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

def create_initial_schema_historical(conn: sqlite3.Connection):
    """创建历史数据库初始架构"""
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

def create_initial_schema_users(conn: sqlite3.Connection):
    """创建用户数据库初始架构"""
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
    
    # API密钥历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_key_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            old_api_key TEXT NOT NULL,
            new_api_key TEXT NOT NULL,
            reason TEXT,
            created_at INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_api_key ON users(api_key)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_user_time ON api_usage(user_id, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quota_usage_user_date ON quota_usage(user_id, date)')

def add_performance_indexes(conn: sqlite3.Connection):
    """添加性能优化索引"""
    cursor = conn.cursor()
    
    # 为价格历史表添加复合索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_price_history_symbol_interval_time 
        ON price_history(symbol, interval_type, timestamp DESC)
    ''')
    
    # 为API使用记录添加复合索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_api_usage_user_endpoint_time 
        ON api_usage(user_id, endpoint, timestamp DESC)
    ''')
    
    # 为技术指标缓存添加复合索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_technical_cache_symbol_type_expires 
        ON technical_indicators_cache(symbol, indicator_type, expires_at DESC)
    ''')

def add_monitoring_tables(conn: sqlite3.Connection):
    """添加监控相关表"""
    cursor = conn.cursor()
    
    # 系统性能监控表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_unit TEXT,
            timestamp INTEGER NOT NULL,
            tags TEXT
        )
    ''')
    
    # 错误日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            stack_trace TEXT,
            context_data TEXT,
            timestamp INTEGER NOT NULL,
            resolved BOOLEAN DEFAULT 0
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_name_time ON system_metrics(metric_name, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_logs_type_time ON error_logs(error_type, timestamp)')

# ==================== 迁移注册 ====================

def setup_migrations():
    """设置所有迁移"""
    from ..config import config
    
    # 主数据库迁移
    main_manager = MigrationManager(config.get_database_url('main').replace('sqlite:///', ''))
    main_manager.add_migration(Migration(
        "001_initial_schema",
        "创建主数据库初始架构",
        create_initial_schema_main
    ))
    main_manager.add_migration(Migration(
        "002_performance_indexes",
        "添加性能优化索引",
        add_performance_indexes
    ))
    main_manager.add_migration(Migration(
        "003_monitoring_tables",
        "添加监控相关表",
        add_monitoring_tables
    ))
    
    # 历史数据库迁移
    historical_manager = MigrationManager(config.get_database_url('historical').replace('sqlite:///', ''))
    historical_manager.add_migration(Migration(
        "001_initial_schema",
        "创建历史数据库初始架构",
        create_initial_schema_historical
    ))
    
    # 用户数据库迁移
    users_manager = MigrationManager(config.get_database_url('users').replace('sqlite:///', ''))
    users_manager.add_migration(Migration(
        "001_initial_schema",
        "创建用户数据库初始架构",
        create_initial_schema_users
    ))
    
    return {
        'main': main_manager,
        'historical': historical_manager,
        'users': users_manager
    }

def run_all_migrations():
    """运行所有数据库的迁移"""
    managers = setup_migrations()
    
    for db_name, manager in managers.items():
        logger.info(f"开始处理 {db_name} 数据库迁移...")
        try:
            manager.apply_migrations()
            status = manager.get_migration_status()
            logger.info(f"{db_name} 数据库迁移完成: {status['applied_count']}/{status['total_migrations']} 已应用")
        except Exception as e:
            logger.error(f"{db_name} 数据库迁移失败: {e}")
            raise

def get_migration_status():
    """获取所有数据库的迁移状态"""
    managers = setup_migrations()
    status = {}
    
    for db_name, manager in managers.items():
        status[db_name] = manager.get_migration_status()
    
    return status

# 导出
__all__ = [
    'Migration',
    'MigrationManager',
    'setup_migrations',
    'run_all_migrations',
    'get_migration_status'
]