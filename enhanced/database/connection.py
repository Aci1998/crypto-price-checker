"""
数据库连接管理

提供数据库连接池和会话管理功能
"""

import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import threading
import logging
from typing import Optional, Dict, Any

from ..config import config
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engines: Dict[str, Any] = {}
        self.session_factories: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialized = False
    
    def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            try:
                # 创建各个数据库的引擎
                self._create_engines()
                
                # 创建会话工厂
                self._create_session_factories()
                
                # 创建表结构
                self._create_tables()
                
                self._initialized = True
                logger.info("数据库初始化完成")
                
            except Exception as e:
                logger.error(f"数据库初始化失败: {e}")
                raise
    
    def _create_engines(self):
        """创建数据库引擎"""
        # 主数据库引擎
        self.engines['main'] = create_engine(
            config.get_database_url('main'),
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'check_same_thread': False,
                'timeout': config.database.CONNECTION_TIMEOUT
            },
            echo=config.api.DEBUG
        )
        
        # 历史数据数据库引擎
        self.engines['historical'] = create_engine(
            config.get_database_url('historical'),
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'check_same_thread': False,
                'timeout': config.database.CONNECTION_TIMEOUT
            },
            echo=config.api.DEBUG
        )
        
        # 用户数据数据库引擎
        self.engines['users'] = create_engine(
            config.get_database_url('users'),
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                'check_same_thread': False,
                'timeout': config.database.CONNECTION_TIMEOUT
            },
            echo=config.api.DEBUG
        )
        
        # 为SQLite启用外键约束
        for engine in self.engines.values():
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                if 'sqlite' in str(engine.url):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=10000")
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.close()
    
    def _create_session_factories(self):
        """创建会话工厂"""
        for db_name, engine in self.engines.items():
            self.session_factories[db_name] = scoped_session(
                sessionmaker(
                    bind=engine,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            )
    
    def _create_tables(self):
        """创建数据库表"""
        try:
            # 在所有数据库中创建表
            for db_name, engine in self.engines.items():
                Base.metadata.create_all(engine)
                logger.info(f"数据库 {db_name} 表结构创建完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    @contextmanager
    def get_session(self, db_name: str = 'main'):
        """获取数据库会话（上下文管理器）"""
        if not self._initialized:
            self.initialize()
        
        if db_name not in self.session_factories:
            raise ValueError(f"未知的数据库: {db_name}")
        
        session = self.session_factories[db_name]()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def get_engine(self, db_name: str = 'main'):
        """获取数据库引擎"""
        if not self._initialized:
            self.initialize()
        
        if db_name not in self.engines:
            raise ValueError(f"未知的数据库: {db_name}")
        
        return self.engines[db_name]
    
    def health_check(self) -> Dict[str, Any]:
        """数据库健康检查"""
        results = {}
        
        for db_name, engine in self.engines.items():
            try:
                with engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("SELECT 1"))
                results[db_name] = {
                    'status': 'healthy',
                    'url': str(engine.url).replace(engine.url.password or '', '***')
                }
            except Exception as e:
                results[db_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        for db_name, engine in self.engines.items():
            try:
                with engine.connect() as conn:
                    # 获取连接池信息
                    pool = engine.pool
                    stats[db_name] = {
                        'pool_size': pool.size(),
                        'checked_in': pool.checkedin(),
                        'checked_out': pool.checkedout(),
                        'overflow': pool.overflow(),
                        'invalid': pool.invalid()
                    }
            except Exception as e:
                stats[db_name] = {'error': str(e)}
        
        return stats
    
    def close_all(self):
        """关闭所有数据库连接"""
        for db_name, session_factory in self.session_factories.items():
            try:
                session_factory.remove()
                logger.info(f"数据库 {db_name} 会话已关闭")
            except Exception as e:
                logger.error(f"关闭数据库 {db_name} 会话失败: {e}")
        
        for db_name, engine in self.engines.items():
            try:
                engine.dispose()
                logger.info(f"数据库 {db_name} 引擎已关闭")
            except Exception as e:
                logger.error(f"关闭数据库 {db_name} 引擎失败: {e}")
        
        self._initialized = False

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 便捷函数
def get_session(db_name: str = 'main'):
    """获取数据库会话"""
    return db_manager.get_session(db_name)

def get_engine(db_name: str = 'main'):
    """获取数据库引擎"""
    return db_manager.get_engine(db_name)

def initialize_database():
    """初始化数据库"""
    db_manager.initialize()

def close_database():
    """关闭数据库连接"""
    db_manager.close_all()

# 数据库健康检查函数
def database_health_check():
    """数据库健康检查"""
    return db_manager.health_check()

# 数据库统计信息函数
def database_stats():
    """获取数据库统计信息"""
    return db_manager.get_stats()

__all__ = [
    'DatabaseManager',
    'db_manager',
    'get_session',
    'get_engine',
    'initialize_database',
    'close_database',
    'database_health_check',
    'database_stats'
]