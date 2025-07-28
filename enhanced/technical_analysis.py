#!/usr/bin/env python3
"""
技术分析模块
实现各种技术指标的计算和分析功能
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

try:
    from .utils import (
        safe_float, safe_int, async_timing_decorator,
        CryptoAgentError, ValidationError
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from utils import (
        safe_float, safe_int, async_timing_decorator,
        CryptoAgentError, ValidationError
    )

logger = logging.getLogger(__name__)


class IndicatorType(Enum):
    """技术指标类型枚举"""
    RSI = "rsi"
    MACD = "macd"
    BOLLINGER_BANDS = "bollinger_bands"
    SMA = "sma"
    EMA = "ema"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    CCI = "cci"
    MOMENTUM = "momentum"


@dataclass
class TechnicalIndicators:
    """技术指标数据结构"""
    symbol: str
    timestamp: datetime
    timeframe: str = "1h"
    
    # 趋势指标
    rsi: Optional[float] = None
    macd: Optional[Dict[str, float]] = None
    
    # 波动性指标
    bollinger_bands: Optional[Dict[str, float]] = None
    
    # 移动平均线
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # 动量指标
    stochastic: Optional[Dict[str, float]] = None
    williams_r: Optional[float] = None
    cci: Optional[float] = None
    momentum: Optional[float] = None
    
    # 成交量指标
    volume_sma: Optional[float] = None
    
    # 计算元数据
    data_points_used: int = 0
    calculation_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    def get_signals(self) -> Dict[str, str]:
        """获取交易信号"""
        signals = {}
        
        # RSI信号
        if self.rsi is not None:
            if self.rsi > 70:
                signals['rsi'] = 'overbought'
            elif self.rsi < 30:
                signals['rsi'] = 'oversold'
            else:
                signals['rsi'] = 'neutral'
        
        # MACD信号
        if self.macd and 'histogram' in self.macd:
            if self.macd['histogram'] > 0:
                signals['macd'] = 'bullish'
            else:
                signals['macd'] = 'bearish'
        
        # 布林带信号
        if self.bollinger_bands:
            # 这里需要当前价格来判断，暂时省略
            signals['bollinger'] = 'neutral'
        
        return signals


class TechnicalAnalysisError(CryptoAgentError):
    """技术分析专用异常"""
    def __init__(self, message: str, indicator: str = None, symbol: str = None):
        super().__init__(message, "TECHNICAL_ANALYSIS_ERROR", {
            'indicator': indicator,
            'symbol': symbol
        })


class TechnicalAnalyzer:
    """技术指标计算器"""
    
    def __init__(self, historical_data_manager=None):
        """
        初始化技术分析器
        
        Args:
            historical_data_manager: 历史数据管理器实例
        """
        self.historical_data_manager = historical_data_manager
        self.supported_indicators = {
            IndicatorType.RSI: self._calculate_rsi,
            IndicatorType.MACD: self._calculate_macd,
            IndicatorType.BOLLINGER_BANDS: self._calculate_bollinger_bands,
            IndicatorType.SMA: self._calculate_sma,
            IndicatorType.EMA: self._calculate_ema,
            IndicatorType.STOCHASTIC: self._calculate_stochastic,
            IndicatorType.WILLIAMS_R: self._calculate_williams_r,
            IndicatorType.CCI: self._calculate_cci,
            IndicatorType.MOMENTUM: self._calculate_momentum
        }
        
        # 默认参数
        self.default_params = {
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2.0,
            'sma_periods': [20, 50],
            'ema_periods': [12, 26],
            'stoch_k': 14,
            'stoch_d': 3,
            'williams_period': 14,
            'cci_period': 20,
            'momentum_period': 10
        }
    
    @async_timing_decorator
    async def analyze(
        self, 
        symbol: str, 
        indicators: Optional[List[Union[str, IndicatorType]]] = None,
        timeframe: str = "1h",
        period: str = "30d",
        current_price: Optional[float] = None,
        **kwargs
    ) -> TechnicalIndicators:
        """
        计算指定币种的技术指标
        
        Args:
            symbol: 币种代码
            indicators: 要计算的指标列表，None表示计算所有指标
            timeframe: 时间框架 (1m, 5m, 15m, 1h, 4h, 1d)
            period: 历史数据周期 (7d, 30d, 90d)
            **kwargs: 指标参数覆盖
        
        Returns:
            TechnicalIndicators: 技术指标结果
        
        Raises:
            TechnicalAnalysisError: 技术分析计算错误
            ValidationError: 参数验证错误
        """
        start_time = datetime.now()
        
        try:
            # 参数验证
            self._validate_parameters(symbol, timeframe, period)
            
            # 获取历史数据
            historical_data = await self._get_historical_data(symbol, timeframe, period, current_price)
            
            if not historical_data or len(historical_data) < 20:
                raise TechnicalAnalysisError(
                    f"历史数据不足，需要至少20个数据点，当前只有{len(historical_data) if historical_data else 0}个",
                    symbol=symbol
                )
            
            # 转换为DataFrame
            df = self._prepare_dataframe(historical_data)
            
            # 确定要计算的指标
            indicators_to_calc = self._resolve_indicators(indicators)
            
            # 合并参数
            params = {**self.default_params, **kwargs}
            
            # 创建结果对象
            result = TechnicalIndicators(
                symbol=symbol,
                timestamp=datetime.now(),
                timeframe=timeframe,
                data_points_used=len(df)
            )
            
            # 计算各项指标
            for indicator in indicators_to_calc:
                try:
                    if indicator in self.supported_indicators:
                        indicator_result = self.supported_indicators[indicator](df, params)
                        self._set_indicator_result(result, indicator, indicator_result)
                    else:
                        logger.warning(f"不支持的指标: {indicator}")
                        
                except Exception as e:
                    logger.error(f"计算指标 {indicator} 时出错: {e}")
                    # 继续计算其他指标，不因单个指标失败而中断
            
            # 记录计算时间
            calculation_time = (datetime.now() - start_time).total_seconds() * 1000
            result.calculation_time_ms = calculation_time
            
            logger.info(f"技术分析完成: {symbol}, 耗时: {calculation_time:.2f}ms")
            
            return result
            
        except Exception as e:
            if isinstance(e, (TechnicalAnalysisError, ValidationError)):
                raise
            else:
                raise TechnicalAnalysisError(f"技术分析计算失败: {str(e)}", symbol=symbol)
    
    def _validate_parameters(self, symbol: str, timeframe: str, period: str):
        """验证输入参数"""
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("币种代码不能为空", "symbol", symbol)
        
        valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
        if timeframe not in valid_timeframes:
            raise ValidationError(f"不支持的时间框架: {timeframe}", "timeframe", timeframe)
        
        valid_periods = ['1d', '7d', '30d', '90d']
        if period not in valid_periods:
            raise ValidationError(f"不支持的历史数据周期: {period}", "period", period)
    
    async def _get_historical_data(self, symbol: str, timeframe: str, period: str, current_price: float = None) -> List[Dict]:
        """获取历史数据"""
        if not self.historical_data_manager:
            # 如果没有历史数据管理器，返回模拟数据用于测试
            return self._generate_mock_data(symbol, 100, current_price)
        
        try:
            return await self.historical_data_manager.get_data(
                symbol=symbol,
                interval=timeframe,
                period=period
            )
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            # 如果获取真实数据失败，使用模拟数据作为后备
            logger.warning(f"使用模拟数据作为后备: {symbol}")
            return self._generate_mock_data(symbol, 100, current_price)
    
    def _prepare_dataframe(self, historical_data: List[Dict]) -> pd.DataFrame:
        """准备DataFrame用于计算"""
        try:
            df = pd.DataFrame(historical_data)
            
            # 确保必要的列存在
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    raise TechnicalAnalysisError(f"历史数据缺少必要字段: {col}")
            
            # 数据类型转换
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 按时间排序
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # 检查数据质量
            if df[['open', 'high', 'low', 'close']].isnull().any().any():
                logger.warning("历史数据中存在空值，将进行前向填充")
                df = df.fillna(method='ffill')
            
            return df
            
        except Exception as e:
            raise TechnicalAnalysisError(f"数据预处理失败: {str(e)}")
    
    def _resolve_indicators(self, indicators: Optional[List[Union[str, IndicatorType]]]) -> List[IndicatorType]:
        """解析要计算的指标列表"""
        if indicators is None:
            return list(self.supported_indicators.keys())
        
        resolved = []
        for indicator in indicators:
            if isinstance(indicator, str):
                try:
                    resolved.append(IndicatorType(indicator.lower()))
                except ValueError:
                    logger.warning(f"未知指标: {indicator}")
            elif isinstance(indicator, IndicatorType):
                resolved.append(indicator)
            else:
                logger.warning(f"无效的指标类型: {type(indicator)}")
        
        return resolved
    
    def _set_indicator_result(self, result: TechnicalIndicators, indicator: IndicatorType, value: Any):
        """设置指标计算结果"""
        if indicator == IndicatorType.RSI:
            result.rsi = value
        elif indicator == IndicatorType.MACD:
            result.macd = value
        elif indicator == IndicatorType.BOLLINGER_BANDS:
            result.bollinger_bands = value
        elif indicator == IndicatorType.SMA:
            if isinstance(value, dict):
                result.sma_20 = value.get('sma_20')
                result.sma_50 = value.get('sma_50')
        elif indicator == IndicatorType.EMA:
            if isinstance(value, dict):
                result.ema_12 = value.get('ema_12')
                result.ema_26 = value.get('ema_26')
        elif indicator == IndicatorType.STOCHASTIC:
            result.stochastic = value
        elif indicator == IndicatorType.WILLIAMS_R:
            result.williams_r = value
        elif indicator == IndicatorType.CCI:
            result.cci = value
        elif indicator == IndicatorType.MOMENTUM:
            result.momentum = value
    
    def _generate_mock_data(self, symbol: str, count: int, current_price: float = None) -> List[Dict]:
        """生成模拟数据用于测试"""
        import random
        
        # 如果提供了当前价格，使用当前价格作为基准
        if current_price and current_price > 0:
            base_price = current_price
        else:
            # 否则使用默认价格
            base_price = 50000 if symbol.upper() == 'BTC' else 3000
        
        data = []
        current_time = int(datetime.now().timestamp()) - count * 3600
        
        # 设置随机种子以确保一致性
        random.seed(hash(symbol) % 1000)
        
        for i in range(count):
            # 简单的随机游走模拟价格，变化幅度较小
            change = random.uniform(-0.02, 0.02)  # 减小变化幅度
            base_price *= (1 + change)
            
            high = base_price * random.uniform(1.001, 1.01)
            low = base_price * random.uniform(0.99, 0.999)
            open_price = base_price * random.uniform(0.998, 1.002)
            close = base_price
            volume = random.uniform(100, 1000)
            
            data.append({
                'timestamp': current_time + i * 3600,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return data
    
    # ==================== 技术指标计算方法 ====================
    
    def _calculate_rsi(self, df: pd.DataFrame, params: Dict) -> float:
        """计算RSI指标"""
        period = params.get('rsi_period', 14)
        
        if len(df) < period + 1:
            raise TechnicalAnalysisError(f"RSI计算需要至少{period + 1}个数据点")
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return safe_float(rsi.iloc[-1])
    
    def _calculate_macd(self, df: pd.DataFrame, params: Dict) -> Dict[str, float]:
        """计算MACD指标"""
        fast_period = params.get('macd_fast', 12)
        slow_period = params.get('macd_slow', 26)
        signal_period = params.get('macd_signal', 9)
        
        if len(df) < slow_period + signal_period:
            raise TechnicalAnalysisError(f"MACD计算需要至少{slow_period + signal_period}个数据点")
        
        ema_fast = df['close'].ewm(span=fast_period).mean()
        ema_slow = df['close'].ewm(span=slow_period).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': safe_float(macd_line.iloc[-1]),
            'signal': safe_float(signal_line.iloc[-1]),
            'histogram': safe_float(histogram.iloc[-1])
        }
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, params: Dict) -> Dict[str, float]:
        """计算布林带指标"""
        period = params.get('bb_period', 20)
        std_dev = params.get('bb_std', 2.0)
        
        if len(df) < period:
            raise TechnicalAnalysisError(f"布林带计算需要至少{period}个数据点")
        
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': safe_float(upper_band.iloc[-1]),
            'middle': safe_float(sma.iloc[-1]),
            'lower': safe_float(lower_band.iloc[-1]),
            'bandwidth': safe_float((upper_band.iloc[-1] - lower_band.iloc[-1]) / sma.iloc[-1] * 100)
        }
    
    def _calculate_sma(self, df: pd.DataFrame, params: Dict) -> Dict[str, float]:
        """计算简单移动平均线"""
        periods = params.get('sma_periods', [20, 50])
        result = {}
        
        for period in periods:
            if len(df) >= period:
                sma = df['close'].rolling(window=period).mean()
                result[f'sma_{period}'] = safe_float(sma.iloc[-1])
        
        return result
    
    def _calculate_ema(self, df: pd.DataFrame, params: Dict) -> Dict[str, float]:
        """计算指数移动平均线"""
        periods = params.get('ema_periods', [12, 26])
        result = {}
        
        for period in periods:
            if len(df) >= period:
                ema = df['close'].ewm(span=period).mean()
                result[f'ema_{period}'] = safe_float(ema.iloc[-1])
        
        return result
    
    def _calculate_stochastic(self, df: pd.DataFrame, params: Dict) -> Dict[str, float]:
        """计算随机指标"""
        k_period = params.get('stoch_k', 14)
        d_period = params.get('stoch_d', 3)
        
        if len(df) < k_period + d_period:
            raise TechnicalAnalysisError(f"随机指标计算需要至少{k_period + d_period}个数据点")
        
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': safe_float(k_percent.iloc[-1]),
            'd': safe_float(d_percent.iloc[-1])
        }
    
    def _calculate_williams_r(self, df: pd.DataFrame, params: Dict) -> float:
        """计算威廉指标"""
        period = params.get('williams_period', 14)
        
        if len(df) < period:
            raise TechnicalAnalysisError(f"威廉指标计算需要至少{period}个数据点")
        
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        return safe_float(williams_r.iloc[-1])
    
    def _calculate_cci(self, df: pd.DataFrame, params: Dict) -> float:
        """计算商品通道指数"""
        period = params.get('cci_period', 20)
        
        if len(df) < period:
            raise TechnicalAnalysisError(f"CCI计算需要至少{period}个数据点")
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        
        return safe_float(cci.iloc[-1])
    
    def _calculate_momentum(self, df: pd.DataFrame, params: Dict) -> float:
        """计算动量指标"""
        period = params.get('momentum_period', 10)
        
        if len(df) < period + 1:
            raise TechnicalAnalysisError(f"动量指标计算需要至少{period + 1}个数据点")
        
        momentum = df['close'] / df['close'].shift(period) * 100
        
        return safe_float(momentum.iloc[-1])


# 导出
__all__ = [
    'TechnicalAnalyzer',
    'TechnicalIndicators', 
    'IndicatorType',
    'TechnicalAnalysisError'
]