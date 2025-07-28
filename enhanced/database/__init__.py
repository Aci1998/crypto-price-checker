#!/usr/bin/env python3
"""
数据库模块
提供数据库管理和迁移功能
"""

from .migrations import (
    Migration,
    MigrationManager,
    setup_migrations,
    run_all_migrations,
    get_migration_status
)

# 导入DatabaseManager类
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from database import DatabaseManager
except ImportError:
    # 如果导入失败，定义一个占位符
    class DatabaseManager:
        def __init__(self):
            pass

# 导出
__all__ = [
    'Migration',
    'MigrationManager',
    'setup_migrations',
    'run_all_migrations',
    'get_migration_status',
    'DatabaseManager'
]