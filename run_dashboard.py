#!/usr/bin/env python3
"""
启动技术分析仪表板服务器
"""

import sys
import os
import uvicorn
from pathlib import Path

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

def main():
    """启动服务器"""
    print("🚀 启动Enhanced Crypto Agent技术分析仪表板...")
    print("=" * 60)
    
    # 确保必要的目录存在
    directories = ['templates', 'static', 'data', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("📁 目录结构检查完成")
    print("🌐 启动Web服务器...")
    print("📊 仪表板地址: http://localhost:8000/dashboard")
    print("📚 API文档地址: http://localhost:8000/docs")
    print("=" * 60)
    
    try:
        # 启动服务器
        uvicorn.run(
            "enhanced.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查端口8000是否被占用，或者依赖包是否安装完整")

if __name__ == "__main__":
    main()