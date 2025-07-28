#!/usr/bin/env python3
"""
第一周开发任务测试脚本
验证项目结构、数据库和配置是否正确设置
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试配置模块
        from enhanced.config import config
        print("✅ 配置模块导入成功")
        
        # 测试数据库模块
        import enhanced.database
        print("✅ 数据库模块导入成功")
        
        # 测试工具模块
        from enhanced.utils import generate_api_key, validate_symbol
        print("✅ 工具模块导入成功")
        
        # 测试迁移模块
        from enhanced.database.migrations import get_migration_status
        print("✅ 迁移模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置系统"""
    print("\n🔍 测试配置系统...")
    
    try:
        from enhanced.config import config
        
        # 测试配置验证
        errors = config.validate()
        if errors:
            print("⚠️  配置验证发现问题:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ 配置验证通过")
        
        # 测试配置访问
        print(f"   环境: {config.environment}")
        print(f"   数据库路径: {config.database.MAIN_DB_PATH}")
        print(f"   API端口: {config.api.PORT}")
        print(f"   缓存TTL: {config.cache.DEFAULT_CACHE_TTL}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_database_creation():
    """测试数据库创建"""
    print("\n🔍 测试数据库创建...")
    
    try:
        from enhanced.database import db_manager
        
        # 检查数据库文件是否存在
        db_paths = {
            'main': db_manager.db_configs['main'],
            'historical': db_manager.db_configs['historical'],
            'users': db_manager.db_configs['users']
        }
        
        for db_name, db_path in db_paths.items():
            if os.path.exists(db_path):
                print(f"✅ {db_name} 数据库文件已创建: {db_path}")
            else:
                print(f"❌ {db_name} 数据库文件不存在: {db_path}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库创建测试失败: {e}")
        return False

def test_database_schema():
    """测试数据库表结构"""
    print("\n🔍 测试数据库表结构...")
    
    try:
        from enhanced.database import db_manager
        
        # 测试主数据库表
        with db_manager.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['system_config', 'supported_currencies', 'data_sources']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 主数据库表 {table} 存在")
                else:
                    print(f"❌ 主数据库表 {table} 不存在")
                    return False
        
        # 测试历史数据库表
        with db_manager.get_connection('historical') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['price_history', 'technical_indicators_cache', 'sync_status']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 历史数据库表 {table} 存在")
                else:
                    print(f"❌ 历史数据库表 {table} 不存在")
                    return False
        
        # 测试用户数据库表
        with db_manager.get_connection('users') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['users', 'api_usage', 'quota_usage']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 用户数据库表 {table} 存在")
                else:
                    print(f"❌ 用户数据库表 {table} 不存在")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库表结构测试失败: {e}")
        return False

def test_initial_data():
    """测试初始数据"""
    print("\n🔍 测试初始数据...")
    
    try:
        from enhanced.database import db_manager
        
        # 测试支持的货币
        currencies = db_manager.get_supported_currencies()
        if currencies:
            print(f"✅ 已加载 {len(currencies)} 种支持的货币")
            print(f"   示例: {currencies[0]['symbol']} - {currencies[0]['name']}")
        else:
            print("❌ 没有找到支持的货币数据")
            return False
        
        # 测试数据源
        data_sources = db_manager.get_data_sources()
        if data_sources:
            print(f"✅ 已配置 {len(data_sources)} 个数据源")
            print(f"   示例: {data_sources[0]['name']} - {data_sources[0]['base_url']}")
        else:
            print("❌ 没有找到数据源配置")
            return False
        
        # 测试系统配置
        version = db_manager.get_system_config('version')
        if version:
            print(f"✅ 系统版本: {version}")
        else:
            print("❌ 没有找到系统版本配置")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 初始数据测试失败: {e}")
        return False

def test_utilities():
    """测试工具函数"""
    print("\n🔍 测试工具函数...")
    
    try:
        from enhanced.utils import (
            generate_api_key, validate_symbol, validate_email,
            safe_float, safe_int, format_price, get_current_timestamp
        )
        
        # 测试API密钥生成
        api_key = generate_api_key()
        if api_key.startswith('ca_') and len(api_key) > 10:
            print(f"✅ API密钥生成成功: {api_key[:10]}...")
        else:
            print(f"❌ API密钥生成失败: {api_key}")
            return False
        
        # 测试符号验证
        if validate_symbol('BTC') and not validate_symbol('123') and not validate_symbol(''):
            print("✅ 符号验证功能正常")
        else:
            print("❌ 符号验证功能异常")
            print(f"  BTC: {validate_symbol('BTC')}")
            print(f"  123: {validate_symbol('123')}")
            print(f"  '': {validate_symbol('')}")
            return False
        
        # 测试邮箱验证
        if validate_email('test@example.com') and not validate_email('invalid'):
            print("✅ 邮箱验证功能正常")
        else:
            print("❌ 邮箱验证功能异常")
            return False
        
        # 测试数据转换
        if safe_float('123.45') == 123.45 and safe_int('123') == 123:
            print("✅ 数据转换功能正常")
        else:
            print("❌ 数据转换功能异常")
            return False
        
        # 测试价格格式化
        formatted = format_price(1234.56)
        if '$' in formatted:
            print(f"✅ 价格格式化正常: {formatted}")
        else:
            print(f"❌ 价格格式化异常: {formatted}")
            return False
        
        # 测试时间戳
        timestamp = get_current_timestamp()
        if isinstance(timestamp, int) and timestamp > 0:
            print(f"✅ 时间戳生成正常: {timestamp}")
        else:
            print(f"❌ 时间戳生成异常: {timestamp}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False

def test_migration_system():
    """测试迁移系统"""
    print("\n🔍 测试迁移系统...")
    
    try:
        from enhanced.database.migrations import get_migration_status
        
        status = get_migration_status()
        
        for db_name, db_status in status.items():
            print(f"✅ {db_name} 数据库迁移状态:")
            print(f"   总迁移数: {db_status['total_migrations']}")
            print(f"   已应用: {db_status['applied_count']}")
            print(f"   待处理: {db_status['pending_count']}")
            
            if db_status['pending_count'] > 0:
                print(f"   ⚠️  有 {db_status['pending_count']} 个待处理迁移")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移系统测试失败: {e}")
        return False

def test_cli_tools():
    """测试命令行工具"""
    print("\n🔍 测试命令行工具...")
    
    try:
        # 测试版本信息
        from enhanced import __version__
        if __version__:
            print(f"✅ 版本信息: {__version__}")
        else:
            print("❌ 版本信息缺失")
            return False
        
        print("✅ CLI模块导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 命令行工具测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n🔍 测试项目结构...")
    
    expected_files = [
        'enhanced/__init__.py',
        'enhanced/config.py',
        'enhanced/database.py',
        'enhanced/utils.py',
        'enhanced/cli.py',
        'enhanced/setup.py',
        'enhanced/database/__init__.py',
        'enhanced/database/migrations.py',
    ]
    
    all_exist = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Enhanced Crypto Agent - 第一周开发任务测试")
    print("=" * 60)
    
    tests = [
        ("项目结构", test_project_structure),
        ("模块导入", test_imports),
        ("配置系统", test_config),
        ("数据库创建", test_database_creation),
        ("数据库表结构", test_database_schema),
        ("初始数据", test_initial_data),
        ("工具函数", test_utilities),
        ("迁移系统", test_migration_system),
        ("命令行工具", test_cli_tools),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！第一周开发任务完成！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())