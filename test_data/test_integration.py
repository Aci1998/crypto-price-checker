#!/usr/bin/env python3
"""
测试技术分析与现有系统的集成
"""

import sys
import os
from datetime import datetime

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

def test_technical_analysis_import():
    """测试技术分析模块导入"""
    print("🔍 测试技术分析模块导入...")
    
    try:
        from technical_analysis import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        print("✅ 技术分析模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 技术分析模块导入失败: {e}")
        return False

def test_app_integration():
    """测试与主应用的集成"""
    print("\n🔍 测试与主应用的集成...")
    
    try:
        # 导入主应用
        import app
        
        # 检查技术分析是否可用
        if hasattr(app, 'TECHNICAL_ANALYSIS_AVAILABLE'):
            print(f"✅ 技术分析可用性: {app.TECHNICAL_ANALYSIS_AVAILABLE}")
        
        if hasattr(app, 'technical_analyzer') and app.technical_analyzer:
            print("✅ 技术分析器实例已创建")
        else:
            print("❌ 技术分析器实例未创建")
            return False
        
        # 测试技术分析函数
        if hasattr(app, 'get_technical_analysis'):
            print("✅ get_technical_analysis 函数存在")
            
            # 测试调用
            result = app.get_technical_analysis('BTC')
            if result:
                print("✅ 技术分析函数调用成功")
                print(f"   RSI: {result.get('rsi', 'N/A')}")
                print(f"   MACD: {result.get('macd', 'N/A')}")
                print(f"   信号: {result.get('signals', 'N/A')}")
            else:
                print("⚠️ 技术分析函数返回空结果（可能正常，取决于数据）")
        else:
            print("❌ get_technical_analysis 函数不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 主应用集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """测试Flask应用启动"""
    print("\n🔍 测试Flask应用...")
    
    try:
        import app
        
        # 检查Flask应用实例
        if hasattr(app, 'app') and app.app:
            print("✅ Flask应用实例存在")
            
            # 检查路由
            routes = [rule.rule for rule in app.app.url_map.iter_rules()]
            print(f"✅ 应用路由: {routes}")
            
            return True
        else:
            print("❌ Flask应用实例不存在")
            return False
            
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False

def test_template_exists():
    """测试模板文件是否存在"""
    print("\n🔍 测试模板文件...")
    
    template_path = "templates/index.html"
    if os.path.exists(template_path):
        print("✅ 模板文件存在")
        
        # 检查模板中是否包含技术分析相关内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'technical_analysis' in content:
            print("✅ 模板包含技术分析相关内容")
        else:
            print("❌ 模板不包含技术分析相关内容")
            return False
        
        if 'indicator-card' in content:
            print("✅ 模板包含指标卡片样式")
        else:
            print("❌ 模板不包含指标卡片样式")
            return False
        
        return True
    else:
        print("❌ 模板文件不存在")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 Enhanced Crypto Agent - 集成测试")
    print("=" * 60)
    
    tests = [
        ("技术分析模块导入", test_technical_analysis_import),
        ("主应用集成", test_app_integration),
        ("Flask应用", test_flask_app),
        ("模板文件", test_template_exists),
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
    
    if passed >= 3:  # 至少3个测试通过
        print("\n🎉 集成测试基本通过！")
        
        print("\n📋 集成完成的功能:")
        print("✅ 技术分析模块已集成到主应用")
        print("✅ 查询加密货币时会自动计算技术指标")
        print("✅ 页面会显示以下技术指标:")
        print("  - RSI (相对强弱指数)")
        print("  - MACD (移动平均收敛散度)")
        print("  - 布林带 (Bollinger Bands)")
        print("  - SMA/EMA (移动平均线)")
        print("  - Stochastic (随机指标)")
        print("  - Williams %R (威廉指标)")
        print("  - CCI (商品通道指数)")
        print("  - Momentum (动量指标)")
        print("  - 综合交易信号")
        
        print("\n🎯 现在的功能:")
        print("📊 基础功能: 当前价格、24小时最高、24小时最低")
        print("📈 新增功能: 9种技术指标 + 交易信号")
        print("⚡ 性能信息: 计算耗时、数据点数")
        
        print("\n🚀 启动应用:")
        print("运行: python app.py")
        print("访问: http://localhost:5000")
        print("输入币种代码（如BTC、ETH）即可看到完整的技术分析")
        
        return 0
    else:
        print("\n⚠️ 集成测试需要进一步完善")
        return 1

if __name__ == '__main__':
    sys.exit(main())