"""
增强版加密货币Agent集成工具包

这个包提供了增强的加密货币价格查询和技术分析功能，
包括历史数据管理、缓存优化、用户认证等企业级特性。
"""

__version__ = "1.1.0"
__author__ = "Crypto Agent Team"
__email__ = "support@crypto-agent.com"

from .config import config

# 版本信息
VERSION_INFO = {
    'version': __version__,
    'features': [
        'Technical Analysis',
        'Historical Data Management', 
        'Enhanced Caching',
        'User Authentication',
        'API Rate Limiting',
        'Performance Monitoring'
    ],
    'supported_indicators': config.get_supported_indicators(),
    'supported_intervals': config.technical_analysis.get_supported_intervals()
}

def get_version_info():
    """获取版本信息"""
    return VERSION_INFO

def health_check():
    """系统健康检查"""
    try:
        # 检查配置
        if not config.validate():
            return {'status': 'error', 'message': '配置验证失败'}
        
        # 检查数据库连接
        # TODO: 实现数据库连接检查
        
        # 检查缓存连接
        # TODO: 实现缓存连接检查
        
        return {
            'status': 'healthy',
            'version': __version__,
            'timestamp': config.logging.LOG_FORMAT,
            'features': VERSION_INFO['features']
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

__all__ = [
    'config',
    'get_version_info',
    'health_check',
    'VERSION_INFO'
]