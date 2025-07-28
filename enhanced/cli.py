#!/usr/bin/env python3
"""
命令行接口模块
提供数据库迁移、系统管理等命令行工具
"""

import argparse
import sys
import logging
from typing import Optional

from . import __version__
from .config import config
from .database.migrations import run_all_migrations, get_migration_status
from .database import db_manager

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def cmd_version(args):
    """显示版本信息"""
    print(f"Enhanced Crypto Agent v{__version__}")
    print(f"环境: {config.environment}")
    print(f"数据库路径: {config.database.main_db_path}")

def cmd_migrate(args):
    """运行数据库迁移"""
    try:
        print("开始数据库迁移...")
        run_all_migrations()
        print("数据库迁移完成!")
    except Exception as e:
        print(f"数据库迁移失败: {e}")
        sys.exit(1)

def cmd_migration_status(args):
    """显示迁移状态"""
    try:
        status = get_migration_status()
        
        print("数据库迁移状态:")
        print("=" * 50)
        
        for db_name, db_status in status.items():
            print(f"\n{db_name.upper()} 数据库:")
            print(f"  总迁移数: {db_status['total_migrations']}")
            print(f"  已应用: {db_status['applied_count']}")
            print(f"  待处理: {db_status['pending_count']}")
            
            if db_status['last_applied']:
                print(f"  最后应用: {db_status['last_applied']}")
            
            if db_status['pending_versions']:
                print(f"  待处理版本: {', '.join(db_status['pending_versions'])}")
        
    except Exception as e:
        print(f"获取迁移状态失败: {e}")
        sys.exit(1)

def cmd_db_stats(args):
    """显示数据库统计信息"""
    try:
        stats = db_manager.get_database_stats()
        
        print("数据库统计信息:")
        print("=" * 50)
        print(f"活跃货币数量: {stats['active_currencies']}")
        print(f"活跃数据源: {stats['active_data_sources']}")
        print(f"价格历史记录: {stats['price_history_records']}")
        print(f"活跃缓存记录: {stats['active_cache_records']}")
        print(f"活跃用户: {stats['active_users']}")
        print(f"24小时API请求: {stats['api_requests_24h']}")
        
    except Exception as e:
        print(f"获取数据库统计失败: {e}")
        sys.exit(1)

def cmd_cleanup(args):
    """清理旧数据"""
    try:
        days = args.days or 90
        print(f"清理 {days} 天前的旧数据...")
        
        result = db_manager.cleanup_old_data(days)
        
        print("数据清理完成:")
        print(f"  删除价格记录: {result['price_records_deleted']}")
        print(f"  删除缓存记录: {result['cache_records_deleted']}")
        print(f"  删除API记录: {result['api_records_deleted']}")
        
    except Exception as e:
        print(f"数据清理失败: {e}")
        sys.exit(1)

def cmd_config_check(args):
    """检查配置"""
    try:
        print("配置检查:")
        print("=" * 50)
        
        # 验证配置
        errors = config.validate()
        
        if errors:
            print("配置错误:")
            for error in errors:
                print(f"  ❌ {error}")
            sys.exit(1)
        else:
            print("✅ 配置验证通过")
        
        # 显示关键配置
        print(f"\n环境: {config.environment}")
        print(f"调试模式: {config.debug}")
        print(f"API端口: {config.api.port}")
        print(f"数据库路径: {config.database.main_db_path}")
        print(f"Redis URL: {config.cache.redis_url}")
        print(f"日志级别: {config.logging.log_level}")
        
    except Exception as e:
        print(f"配置检查失败: {e}")
        sys.exit(1)

def cmd_health_check(args):
    """系统健康检查"""
    try:
        from . import health_check
        
        result = health_check()
        
        print("系统健康检查:")
        print("=" * 50)
        print(f"状态: {result['status']}")
        print(f"版本: {result.get('version', 'N/A')}")
        print(f"时间戳: {result['timestamp']}")
        
        if result['status'] == 'healthy':
            print("✅ 系统运行正常")
            if 'features' in result:
                print(f"功能: {', '.join(result['features'])}")
        else:
            print("❌ 系统存在问题")
            if 'errors' in result:
                for error in result['errors']:
                    print(f"  - {error}")
            if 'error' in result:
                print(f"  错误: {result['error']}")
            sys.exit(1)
        
    except Exception as e:
        print(f"健康检查失败: {e}")
        sys.exit(1)

def cmd_init_db(args):
    """初始化数据库"""
    try:
        print("初始化数据库...")
        
        # 运行迁移
        run_all_migrations()
        
        # 显示统计信息
        stats = db_manager.get_database_stats()
        
        print("数据库初始化完成!")
        print(f"支持的货币: {stats['active_currencies']}")
        print(f"配置的数据源: {stats['active_data_sources']}")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)

def main():
    """主命令行入口"""
    parser = argparse.ArgumentParser(
        description="Enhanced Crypto Agent 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细输出'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 版本命令
    version_parser = subparsers.add_parser('version', help='显示版本信息')
    version_parser.set_defaults(func=cmd_version)
    
    # 数据库相关命令
    db_group = subparsers.add_parser('db', help='数据库管理命令')
    db_subparsers = db_group.add_subparsers(dest='db_command')
    
    # 迁移命令
    migrate_parser = db_subparsers.add_parser('migrate', help='运行数据库迁移')
    migrate_parser.set_defaults(func=cmd_migrate)
    
    # 迁移状态命令
    status_parser = db_subparsers.add_parser('migration-status', help='显示迁移状态')
    status_parser.set_defaults(func=cmd_migration_status)
    
    # 数据库统计命令
    stats_parser = db_subparsers.add_parser('stats', help='显示数据库统计')
    stats_parser.set_defaults(func=cmd_db_stats)
    
    # 数据清理命令
    cleanup_parser = db_subparsers.add_parser('cleanup', help='清理旧数据')
    cleanup_parser.add_argument('--days', type=int, default=90, help='保留天数 (默认: 90)')
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # 初始化数据库命令
    init_parser = db_subparsers.add_parser('init', help='初始化数据库')
    init_parser.set_defaults(func=cmd_init_db)
    
    # 配置检查命令
    config_parser = subparsers.add_parser('config', help='检查配置')
    config_parser.set_defaults(func=cmd_config_check)
    
    # 健康检查命令
    health_parser = subparsers.add_parser('health', help='系统健康检查')
    health_parser.set_defaults(func=cmd_health_check)
    
    # 解析参数
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 执行命令
    if hasattr(args, 'func'):
        args.func(args)
    elif args.command == 'db':
        if hasattr(args, 'db_command') and args.db_command:
            # 数据库子命令已经设置了func
            pass
        else:
            db_group.print_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()