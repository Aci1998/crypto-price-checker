#!/usr/bin/env python3
"""
Enhanced Crypto Agent 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Enhanced Crypto Currency Agent Integration Toolkit"

# 读取requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="enhanced-crypto-agent",
    version="1.1.0",
    author="Crypto Agent Team",
    author_email="team@crypto-agent.com",
    description="Enhanced crypto currency agent integration toolkit with technical analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/crypto-agent/enhanced-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心依赖
        "Flask>=2.3.0",
        "FastAPI>=0.104.0",
        "uvicorn>=0.24.0",
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        
        # 数据处理和分析
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "TA-Lib>=0.4.28",
        "scipy>=1.11.0",
        
        # 数据库
        "SQLAlchemy>=2.0.0",
        "alembic>=1.12.0",
        
        # 缓存
        "redis>=5.0.0",
        "hiredis>=2.2.0",
        
        # 认证和安全
        "PyJWT>=2.8.0",
        "bcrypt>=4.1.0",
        "cryptography>=41.0.0",
        
        # HTTP客户端
        "httpx>=0.25.0",
        "aiohttp>=3.9.0",
        
        # 配置管理
        "python-dotenv>=1.0.0",
        "python-decouple>=3.8",
        
        # 日志和监控
        "structlog>=23.2.0",
        "prometheus-client>=0.19.0",
        
        # 时间处理
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
        
        # JSON处理
        "orjson>=3.9.0",
        
        # 性能监控
        "psutil>=5.9.0",
        
        # 网络请求重试
        "tenacity>=8.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "pre-commit>=3.6.0",
            "factory-boy>=3.3.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "sentry-sdk>=1.38.0",
        ],
        "visualization": [
            "plotly>=5.17.0",
            "matplotlib>=3.8.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crypto-agent-enhanced=enhanced.cli:main",
            "crypto-agent-migrate=enhanced.database.migrations:run_all_migrations",
        ],
    },
    include_package_data=True,
    package_data={
        "enhanced": [
            "config/*.yaml",
            "templates/*.html",
            "static/*",
        ],
    },
    zip_safe=False,
    keywords="cryptocurrency, trading, technical-analysis, api, blockchain, bitcoin, ethereum",
    project_urls={
        "Bug Reports": "https://github.com/crypto-agent/enhanced-toolkit/issues",
        "Source": "https://github.com/crypto-agent/enhanced-toolkit",
        "Documentation": "https://crypto-agent.readthedocs.io/",
    },
)