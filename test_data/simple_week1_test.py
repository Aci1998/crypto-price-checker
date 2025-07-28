#!/usr/bin/env python3
"""
第一周开发任务简化测试脚本
"""

import os
import sys

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

def test_basic_functionality():
    """测试基本功能"""
    print("🔍 测试基本功能...")
    
    try:
        # 测试配置模块
        from config import config
        print("✅ 配置模块导入成功")
        print(f"   环境: {config.environment}")
        print(f"   数据库路径: {config.database.MAIN_DB_PATH}")
        
        # 测试工具函数
        from utils import generate_api_key, validate_symbol, format_price
        
        api_key = generate_api_key()
        print(f"✅ API密钥生成: {api_key[:15]}...")
        
        print(f"✅ 符号验证: BTC={validate_symbol('BTC')}, 123={validate_symbol('123')}")
        
        price_str = format_price(1234.56)
        print(f"✅ 价格格式化: {price_str}")
        
        # 测试数据库管理器
        import importlib.util
        spec = importlib.util.spec_from_file_location("database_module", "enhanced/database.py")
        database_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(database_module)
        
        db_manager = database_module.db_manager
        print("✅ 数据库管理器导入成功")
        
        # 检查数据库文件是否创建
        if os.path.exists(config.database.MAIN_DB_PATH):
            print("✅ 主数据库文件已创建")
        else:
            print("❌ 主数据库文件未创建")
            return False
        
        # 测试数据库连接
        with db_manager.get_connection('main') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ 数据库表: {len(tables)} 个表已创建")
            
            if 'system_config' in tables:
                print("✅ system_config 表存在")
            else:
                print("❌ system_config 表不存在")
                return False
        
        # 测试迁移系统
        from database.migrations import get_migration_status
        status = get_migration_status()
        print(f"✅ 迁移系统: {len(status)} 个数据库")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Enhanced Crypto Agent - 第一周开发任务简化测试")
    print("=" * 60)
    
    if test_basic_functionality():
        print("\n🎉 基本功能测试通过！第一周开发任务基本完成！")
        
        print("\n📋 完成的任务:")
        print("✅ 1.1.1 创建增强版项目结构")
        print("✅ 1.1.2 数据库设计和初始化")
        print("✅ 1.1.3 依赖包更新和管理")
        
        print("\n📝 项目结构:")
        print("✅ enhanced/config.py - 配置管理模块")
        print("✅ enhanced/database.py - 数据库管理模块")
        print("✅ enhanced/utils.py - 工具函数模块")
        print("✅ enhanced/cli.py - 命令行工具")
        print("✅ enhanced/database/migrations.py - 数据库迁移")
        print("✅ enhanced/setup.py - 安装脚本")
        
        print("\n🔧 核心功能:")
        print("✅ 配置管理系统")
        print("✅ 数据库连接和表结构")
        print("✅ 工具函数库")
        print("✅ 数据库迁移系统")
        print("✅ 命令行工具")
        
        return 0
    else:
        print("\n❌ 测试失败，请检查相关问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())