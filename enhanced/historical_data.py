#!/usr/bin/env python3
"""
历史数据管理模块
负责获取、存储和管理加密货币的历史价格数据
"""

import asyncio
import aiohttp
import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

try:
    from .config import config
except ImportError:
    from config import config
try:
    from .utils import (
        async_timing_decorator, retry_decorator,
        CryptoAgentError, APIError, DatabaseError
    )
except ImportError:
    from utils import (
        async_timing_decorator, retry_decorator,
        CryptoAgentError, APIError, DatabaseError
    )

logger = logging.getLogger(__name__)


class HistoricalDataError(CryptoAgentError):
    """历史数据专用异常"""
    def __init__(self, message: str, symbol: str = None, source: str = None):
        super().__init__(message, "HISTORICAL_DATA_ERROR", {
            'symbol': symbol,
            'source': source
        })


class DataSource:
    """数据源基类"""
    
    def __init__(self, name: str, base_url: str, rate_limit: int = 60):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
    async def fetch_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """获取历史数据 - 子类需要实现"""
        raise NotImplementedError
    
    async def _rate_limit_check(self):
        """速率限制检查"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.now().timestamp()


class BinanceDataSource(DataSource):
    """Binance数据源"""
    
    def __init__(self):
        super().__init__("Binance", "https://api.binance.com/api/v3", 1200)
        
        # 时间间隔映射
        self.interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1w'
        }
    
    @retry_decorator(max_attempts=3, delay=1.0)
    async def fetch_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """从Binance获取历史数据"""
        await self._rate_limit_check()
        
        # 转换符号格式
        binance_symbol = symbol.upper().replace('/', '')
        binance_interval = self.interval_map.get(interval, '1h')
        
        url = f"{self.base_url}/klines"
        params = {
            'symbol': binance_symbol,
            'interval': binance_interval,
            'startTime': start_time * 1000,  # Binance使用毫秒
            'endTime': end_time * 1000,
            'limit': 1000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        raise APIError(f"Binance API错误: {response.status}", response.status)
                    
                    data = await response.json()
                    
                    return [
                        {
                            'timestamp': int(item[0]) // 1000,  # 转换为秒
                            'open': float(item[1]),
                            'high': float(item[2]),
                            'low': float(item[3]),
                            'close': float(item[4]),
                            'volume': float(item[5]),
                            'symbol': symbol,
                            'interval': interval,
                            'source': self.name
                        }
                        for item in data
                    ]
                    
        except aiohttp.ClientError as e:
            raise APIError(f"Binance网络请求失败: {str(e)}", source=self.name)
        except Exception as e:
            raise HistoricalDataError(f"Binance数据获取失败: {str(e)}", symbol, self.name)


class OKXDataSource(DataSource):
    """OKX数据源"""
    
    def __init__(self):
        super().__init__("OKX", "https://www.okx.com/api/v5", 600)
        
        self.interval_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D',
            '1w': '1W'
        }
    
    @retry_decorator(max_attempts=3, delay=1.0)
    async def fetch_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """从OKX获取历史数据"""
        await self._rate_limit_check()
        
        # 转换符号格式
        okx_symbol = symbol.upper().replace('/', '-')
        okx_interval = self.interval_map.get(interval, '1H')
        
        url = f"{self.base_url}/market/history-candles"
        params = {
            'instId': okx_symbol,
            'bar': okx_interval,
            'after': str(start_time * 1000),
            'before': str(end_time * 1000),
            'limit': '300'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        raise APIError(f"OKX API错误: {response.status}", response.status)
                    
                    result = await response.json()
                    
                    if result.get('code') != '0':
                        raise APIError(f"OKX API返回错误: {result.get('msg')}")
                    
                    data = result.get('data', [])
                    
                    return [
                        {
                            'timestamp': int(item[0]) // 1000,  # 转换为秒
                            'open': float(item[1]),
                            'high': float(item[2]),
                            'low': float(item[3]),
                            'close': float(item[4]),
                            'volume': float(item[5]),
                            'symbol': symbol,
                            'interval': interval,
                            'source': self.name
                        }
                        for item in data
                    ]
                    
        except aiohttp.ClientError as e:
            raise APIError(f"OKX网络请求失败: {str(e)}", source=self.name)
        except Exception as e:
            raise HistoricalDataError(f"OKX数据获取失败: {str(e)}", symbol, self.name)


class CoinGeckoDataSource(DataSource):
    """CoinGecko数据源"""
    
    def __init__(self):
        super().__init__("CoinGecko", "https://api.coingecko.com/api/v3", 50)
        
        # CoinGecko的币种ID映射
        self.coin_id_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'LTC': 'litecoin',
            'XRP': 'ripple',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'MATIC': 'matic-network',
            'AVAX': 'avalanche-2',
            'DOGE': 'dogecoin',
            'SHIB': 'shiba-inu',
            'UNI': 'uniswap',
            'ATOM': 'cosmos'
        }
    
    @retry_decorator(max_attempts=3, delay=2.0)
    async def fetch_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """从CoinGecko获取历史数据"""
        await self._rate_limit_check()
        
        # 获取币种ID
        coin_id = self.coin_id_map.get(symbol.upper())
        if not coin_id:
            raise HistoricalDataError(f"CoinGecko不支持币种: {symbol}", symbol, self.name)
        
        # CoinGecko只支持日线数据
        if interval not in ['1d']:
            raise HistoricalDataError(f"CoinGecko不支持时间间隔: {interval}", symbol, self.name)
        
        url = f"{self.base_url}/coins/{coin_id}/market_chart/range"
        params = {
            'vs_currency': 'usd',
            'from': start_time,
            'to': end_time
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        raise APIError(f"CoinGecko API错误: {response.status}", response.status)
                    
                    data = await response.json()
                    
                    prices = data.get('prices', [])
                    volumes = data.get('total_volumes', [])
                    
                    # 合并价格和成交量数据
                    result = []
                    for i, (timestamp_ms, price) in enumerate(prices):
                        timestamp = int(timestamp_ms) // 1000
                        volume = volumes[i][1] if i < len(volumes) else 0
                        
                        result.append({
                            'timestamp': timestamp,
                            'open': price,  # CoinGecko只提供收盘价
                            'high': price,
                            'low': price,
                            'close': price,
                            'volume': volume,
                            'symbol': symbol,
                            'interval': interval,
                            'source': self.name
                        })
                    
                    return result
                    
        except aiohttp.ClientError as e:
            raise APIError(f"CoinGecko网络请求失败: {str(e)}", source=self.name)
        except Exception as e:
            raise HistoricalDataError(f"CoinGecko数据获取失败: {str(e)}", symbol, self.name)


class HistoricalDataManager:
    """历史数据管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.database.HISTORICAL_DB_PATH
        self.init_database()
        
        # 初始化数据源
        self.data_sources = [
            BinanceDataSource(),
            OKXDataSource(),
            CoinGeckoDataSource()
        ]
        
        # 缓存设置
        self.cache_ttl = 3600  # 1小时缓存
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 价格历史数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        open_price REAL NOT NULL,
                        high_price REAL NOT NULL,
                        low_price REAL NOT NULL,
                        close_price REAL NOT NULL,
                        volume REAL NOT NULL,
                        interval_type TEXT NOT NULL,
                        data_source TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        UNIQUE(symbol, timestamp, interval_type, data_source)
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_price_history_symbol_time 
                    ON price_history(symbol, timestamp)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_price_history_interval 
                    ON price_history(interval_type, timestamp)
                ''')
                
                conn.commit()
                logger.info("历史数据数据库初始化完成")
                
        except Exception as e:
            raise DatabaseError(f"历史数据数据库初始化失败: {str(e)}")
    
    @async_timing_decorator
    async def get_data(
        self, 
        symbol: str, 
        interval: str = '1h', 
        period: str = '30d',
        force_refresh: bool = False
    ) -> List[Dict]:
        """
        获取历史数据
        
        Args:
            symbol: 币种代码
            interval: 时间间隔
            period: 历史数据周期
            force_refresh: 强制刷新数据
        
        Returns:
            List[Dict]: 历史价格数据
        """
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = self._parse_period(period, end_time)
            
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            # 如果不强制刷新，先尝试从数据库获取
            if not force_refresh:
                local_data = self._get_local_data(symbol, interval, start_timestamp, end_timestamp)
                if self._is_data_sufficient(local_data, start_timestamp, end_timestamp, interval):
                    logger.info(f"从本地数据库获取 {symbol} 历史数据: {len(local_data)} 条记录")
                    return local_data
            
            # 从API获取数据
            api_data = await self._fetch_from_apis(symbol, interval, start_timestamp, end_timestamp)
            
            if api_data:
                # 保存到数据库
                self._save_to_database(api_data)
                logger.info(f"从API获取并保存 {symbol} 历史数据: {len(api_data)} 条记录")
                return api_data
            else:
                # 如果API获取失败，返回本地数据（如果有的话）
                local_data = self._get_local_data(symbol, interval, start_timestamp, end_timestamp)
                if local_data:
                    logger.warning(f"API获取失败，返回本地缓存数据: {len(local_data)} 条记录")
                    return local_data
                else:
                    raise HistoricalDataError(f"无法获取 {symbol} 的历史数据", symbol)
            
        except Exception as e:
            if isinstance(e, HistoricalDataError):
                raise
            else:
                raise HistoricalDataError(f"获取历史数据失败: {str(e)}", symbol)
    
    def _parse_period(self, period: str, end_time: datetime) -> datetime:
        """解析时间周期字符串"""
        period_map = {
            '1d': timedelta(days=1),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
            '90d': timedelta(days=90)
        }
        
        if period not in period_map:
            raise ValueError(f"不支持的时间周期: {period}")
        
        return end_time - period_map[period]
    
    def _get_local_data(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """从本地数据库获取数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, open_price, high_price, low_price, close_price, volume
                    FROM price_history
                    WHERE symbol = ? AND interval_type = ? 
                    AND timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp
                ''', (symbol, interval, start_time, end_time))
                
                rows = cursor.fetchall()
                
                return [
                    {
                        'timestamp': row[0],
                        'open': row[1],
                        'high': row[2],
                        'low': row[3],
                        'close': row[4],
                        'volume': row[5]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"从数据库获取数据失败: {e}")
            return []
    
    def _is_data_sufficient(self, data: List[Dict], start_time: int, end_time: int, interval: str) -> bool:
        """检查数据是否充足"""
        if not data:
            return False
        
        # 计算期望的数据点数量
        interval_seconds = self._interval_to_seconds(interval)
        expected_points = (end_time - start_time) // interval_seconds
        
        # 如果实际数据点数量达到期望的80%以上，认为数据充足
        return len(data) >= expected_points * 0.8
    
    def _interval_to_seconds(self, interval: str) -> int:
        """将时间间隔转换为秒数"""
        interval_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400,
            '1w': 604800
        }
        return interval_map.get(interval, 3600)
    
    async def _fetch_from_apis(self, symbol: str, interval: str, start_time: int, end_time: int) -> List[Dict]:
        """从API获取数据"""
        for source in self.data_sources:
            try:
                logger.info(f"尝试从 {source.name} 获取 {symbol} 数据")
                data = await source.fetch_data(symbol, interval, start_time, end_time)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"从 {source.name} 获取数据失败: {e}")
                continue
        
        return []
    
    def _save_to_database(self, data: List[Dict]):
        """保存数据到数据库"""
        if not data:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = int(datetime.now().timestamp())
                
                for item in data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO price_history 
                        (symbol, timestamp, open_price, high_price, low_price, close_price, 
                         volume, interval_type, data_source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['symbol'],
                        item['timestamp'],
                        item['open'],
                        item['high'],
                        item['low'],
                        item['close'],
                        item['volume'],
                        item['interval'],
                        item['source'],
                        current_time
                    ))
                
                conn.commit()
                logger.info(f"保存 {len(data)} 条历史数据到数据库")
                
        except Exception as e:
            logger.error(f"保存数据到数据库失败: {e}")
            raise DatabaseError(f"保存历史数据失败: {str(e)}")
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM price_history WHERE timestamp < ?', (cutoff_time,))
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"清理了 {deleted_count} 条过期历史数据")
                return deleted_count
                
        except Exception as e:
            logger.error(f"清理历史数据失败: {e}")
            raise DatabaseError(f"清理历史数据失败: {str(e)}")
    
    def get_data_stats(self) -> Dict:
        """获取数据统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总记录数
                cursor.execute('SELECT COUNT(*) FROM price_history')
                total_records = cursor.fetchone()[0]
                
                # 按币种统计
                cursor.execute('''
                    SELECT symbol, COUNT(*) as count 
                    FROM price_history 
                    GROUP BY symbol 
                    ORDER BY count DESC
                ''')
                symbol_stats = cursor.fetchall()
                
                # 按数据源统计
                cursor.execute('''
                    SELECT data_source, COUNT(*) as count 
                    FROM price_history 
                    GROUP BY data_source
                ''')
                source_stats = cursor.fetchall()
                
                return {
                    'total_records': total_records,
                    'symbols': dict(symbol_stats),
                    'sources': dict(source_stats)
                }
                
        except Exception as e:
            logger.error(f"获取数据统计失败: {e}")
            return {}


# 导出
__all__ = [
    'HistoricalDataManager',
    'HistoricalDataError',
    'BinanceDataSource',
    'OKXDataSource', 
    'CoinGeckoDataSource'
]