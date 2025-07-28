#!/usr/bin/env python3
"""
启动增强版加密货币查询应用
集成了技术分析功能
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:5000')

def main():
    """启动应用"""
    print("🚀 启动Enhanced Crypto Agent - 增强版加密货币查询工具")
    print("=" * 70)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return 1
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = [
        'app.py',
        'templates/index.html',
        'enhanced/technical_analysis.py',
        'enhanced/utils.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return 1
    
    print("✅ 必要文件检查通过")
    
    # 检查技术分析模块
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))
        from technical_analysis import TechnicalAnalyzer
        print("✅ 技术分析模块加载成功")
    except ImportError as e:
        print(f"⚠️ 技术分析模块加载失败: {e}")
        print("   应用仍可运行，但不会显示技术指标")
    
    print("\n📊 功能说明:")
    print("🔸 基础功能: 实时价格、24小时最高/最低价格")
    print("🔸 技术分析: RSI、MACD、布林带、移动平均线等9种指标")
    print("🔸 交易信号: 基于技术指标的买卖信号提示")
    print("🔸 支持币种: BTC、ETH、ADA、DOT、LINK等主流币种")
    
    print("\n🌐 启动Web服务器...")
    print("📱 应用地址: http://localhost:5000")
    print("🔄 自动打开浏览器...")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 70)
    
    # 延迟打开浏览器
    Timer(2.0, open_browser).start()
    
    try:
        # 启动Flask应用
        import app
        app.app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # 生产模式
            use_reloader=False  # 避免重复启动
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("请检查端口5000是否被占用")
        return 1

if __name__ == "__main__":
    sys.exit(main())