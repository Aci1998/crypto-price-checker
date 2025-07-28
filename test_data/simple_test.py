#!/usr/bin/env python3
"""
简化的第一周测试脚本
"""

import os
import sys
from pathlib import Path

# 设置开发环境
os.environ['FLASK_ENV'] = 'development'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """测试基本导入"""
    try:
        from enhanced.config import config
        from enhanced.database.models import User, PriceHistory
        from enhanced.database.connection import DatabaseManager
        print("✅ 基本导入测试通过")
        return True
    except Exception as e:
        print(f"❌ 基本导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    try:
        from enhanced.config import config
        if config.validate():
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败")
            return False
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_database_basic():
    """测试数据库基本功能"""
    try:
        from enhanced.database.connection import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.initialize()
        print("✅ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def main():
    print("🚀 第一周开发成果简化测试")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config,
        test_database_basic
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 第一周核心功能开发完成！")
        print("\n✅ 完成的任务:")
        print("  - ✅ 创建增强版项目结构")
        print("  - ✅ 实现配置管理模块")
        print("  - ✅ 设计数据库表结构")
        print("  - ✅ 实现数据库连接管理")
        print("  - ✅ 创建数据库迁移系统")
        print("  - ✅ 更新项目依赖")
        
        print("\n🔄 下周任务:")
        print("  - 实现技术指标计算器")
        print("  - 开发技术分析API接口")
        print("  - 创建历史数据管理器")
        
        return True
    else:
        print("⚠️  部分功能需要进一步完善")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)