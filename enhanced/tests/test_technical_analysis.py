#!/usr/bin/env python3
"""
技术分析模块测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from technical_analysis import (
    TechnicalAnalyzer, TechnicalIndicators, IndicatorType,
    TechnicalAnalysisError
)


class TestTechnicalAnalyzer:
    """技术分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建技术分析器实例"""
        return TechnicalAnalyzer()
    
    @pytest.fixture
    def sample_data(self):
        """创建测试用的历史数据"""
        # 生成100个数据点的模拟数据
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        np.random.seed(42)  # 固定随机种子以确保测试结果一致
        
        # 生成随机游走价格数据
        base_price = 50000
        price_changes = np.random.normal(0, 0.02, 100)  # 2%的标准差
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # 生成OHLC数据
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = price * (1 + np.random.normal(0, 0.005))
            volume = np.random.uniform(100, 1000)
            
            data.append({
                'timestamp': int(date.timestamp()),
                'open': open_price,
                'high': high,
                'low': low,
                'close': price,
                'volume': volume
            })
        
        return data
    
    def test_rsi_calculation(self, analyzer, sample_data):
        """测试RSI计算"""
        df = pd.DataFrame(sample_data)
        
        # 测试RSI计算
        rsi = analyzer._calculate_rsi(df, {'rsi_period': 14})
        
        # RSI应该在0-100之间
        assert 0 <= rsi <= 100
        assert isinstance(rsi, float)
        
        # 测试数据不足的情况
        short_df = df.head(10)
        with pytest.raises(TechnicalAnalysisError):
            analyzer._calculate_rsi(short_df, {'rsi_period': 14})
    
    def test_macd_calculation(self, analyzer, sample_data):
        """测试MACD计算"""
        df = pd.DataFrame(sample_data)
        
        macd = analyzer._calculate_macd(df, {
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        })
        
        # 检查返回的字典结构
        assert isinstance(macd, dict)
        assert 'macd' in macd
        assert 'signal' in macd
        assert 'histogram' in macd
        
        # 检查数值类型
        assert isinstance(macd['macd'], float)
        assert isinstance(macd['signal'], float)
        assert isinstance(macd['histogram'], float)
        
        # 测试数据不足的情况
        short_df = df.head(20)
        with pytest.raises(TechnicalAnalysisError):
            analyzer._calculate_macd(short_df, {
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9
            })
    
    def test_bollinger_bands_calculation(self, analyzer, sample_data):
        """测试布林带计算"""
        df = pd.DataFrame(sample_data)
        
        bb = analyzer._calculate_bollinger_bands(df, {
            'bb_period': 20,
            'bb_std': 2.0
        })
        
        # 检查返回的字典结构
        assert isinstance(bb, dict)
        assert 'upper' in bb
        assert 'middle' in bb
        assert 'lower' in bb
        assert 'bandwidth' in bb
        
        # 上轨应该大于中轨，中轨应该大于下轨
        assert bb['upper'] > bb['middle'] > bb['lower']
        
        # 带宽应该为正数
        assert bb['bandwidth'] > 0
    
    def test_sma_calculation(self, analyzer, sample_data):
        """测试简单移动平均线计算"""
        df = pd.DataFrame(sample_data)
        
        sma = analyzer._calculate_sma(df, {'sma_periods': [20, 50]})
        
        # 检查返回的字典结构
        assert isinstance(sma, dict)
        assert 'sma_20' in sma
        assert 'sma_50' in sma
        
        # 检查数值类型
        assert isinstance(sma['sma_20'], float)
        assert isinstance(sma['sma_50'], float)
        
        # SMA值应该在合理范围内（接近最近的价格）
        recent_price = df['close'].iloc[-1]
        assert abs(sma['sma_20'] - recent_price) / recent_price < 0.5  # 50%的容差
    
    def test_ema_calculation(self, analyzer, sample_data):
        """测试指数移动平均线计算"""
        df = pd.DataFrame(sample_data)
        
        ema = analyzer._calculate_ema(df, {'ema_periods': [12, 26]})
        
        # 检查返回的字典结构
        assert isinstance(ema, dict)
        assert 'ema_12' in ema
        assert 'ema_26' in ema
        
        # 检查数值类型
        assert isinstance(ema['ema_12'], float)
        assert isinstance(ema['ema_26'], float)
    
    def test_stochastic_calculation(self, analyzer, sample_data):
        """测试随机指标计算"""
        df = pd.DataFrame(sample_data)
        
        stoch = analyzer._calculate_stochastic(df, {
            'stoch_k': 14,
            'stoch_d': 3
        })
        
        # 检查返回的字典结构
        assert isinstance(stoch, dict)
        assert 'k' in stoch
        assert 'd' in stoch
        
        # K和D值应该在0-100之间
        assert 0 <= stoch['k'] <= 100
        assert 0 <= stoch['d'] <= 100
    
    def test_williams_r_calculation(self, analyzer, sample_data):
        """测试威廉指标计算"""
        df = pd.DataFrame(sample_data)
        
        williams_r = analyzer._calculate_williams_r(df, {'williams_period': 14})
        
        # 威廉指标应该在-100到0之间
        assert -100 <= williams_r <= 0
        assert isinstance(williams_r, float)
    
    def test_cci_calculation(self, analyzer, sample_data):
        """测试商品通道指数计算"""
        df = pd.DataFrame(sample_data)
        
        cci = analyzer._calculate_cci(df, {'cci_period': 20})
        
        # CCI可以是任何值，但应该是浮点数
        assert isinstance(cci, float)
        # 通常CCI在-200到200之间，但可能超出这个范围
        assert -500 <= cci <= 500  # 宽松的范围检查
    
    def test_momentum_calculation(self, analyzer, sample_data):
        """测试动量指标计算"""
        df = pd.DataFrame(sample_data)
        
        momentum = analyzer._calculate_momentum(df, {'momentum_period': 10})
        
        # 动量指标应该是正数（价格比率 * 100）
        assert isinstance(momentum, float)
        assert momentum > 0  # 应该是正数
    
    @pytest.mark.asyncio
    async def test_analyze_method(self, analyzer, sample_data):
        """测试完整的分析方法"""
        # 模拟历史数据管理器
        class MockHistoricalDataManager:
            async def get_data(self, symbol, interval, period):
                return sample_data
        
        analyzer.historical_data_manager = MockHistoricalDataManager()
        
        # 测试分析所有指标
        result = await analyzer.analyze('BTC', timeframe='1h', period='30d')
        
        # 检查返回的结果类型
        assert isinstance(result, TechnicalIndicators)
        assert result.symbol == 'BTC'
        assert result.timeframe == '1h'
        assert result.data_points_used == len(sample_data)
        
        # 检查各项指标是否计算
        assert result.rsi is not None
        assert result.macd is not None
        assert result.bollinger_bands is not None
        assert result.sma_20 is not None
        assert result.ema_12 is not None
        
        # 检查计算时间
        assert result.calculation_time_ms is not None
        assert result.calculation_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_specific_indicators(self, analyzer, sample_data):
        """测试分析特定指标"""
        class MockHistoricalDataManager:
            async def get_data(self, symbol, interval, period):
                return sample_data
        
        analyzer.historical_data_manager = MockHistoricalDataManager()
        
        # 只计算RSI和MACD
        result = await analyzer.analyze(
            'BTC', 
            indicators=['rsi', 'macd'],
            timeframe='1h', 
            period='30d'
        )
        
        # 应该只有指定的指标被计算
        assert result.rsi is not None
        assert result.macd is not None
        # 其他指标应该为None
        assert result.bollinger_bands is None
        assert result.stochastic is None
    
    @pytest.mark.asyncio
    async def test_analyze_insufficient_data(self, analyzer):
        """测试数据不足的情况"""
        # 模拟数据不足的情况
        class MockHistoricalDataManager:
            async def get_data(self, symbol, interval, period):
                return []  # 返回空数据
        
        analyzer.historical_data_manager = MockHistoricalDataManager()
        
        with pytest.raises(TechnicalAnalysisError):
            await analyzer.analyze('BTC', timeframe='1h', period='30d')
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_parameters(self, analyzer):
        """测试无效参数"""
        with pytest.raises(Exception):  # 应该抛出验证错误
            await analyzer.analyze('', timeframe='invalid', period='invalid')
    
    def test_technical_indicators_to_dict(self, sample_data):
        """测试TechnicalIndicators转字典"""
        indicators = TechnicalIndicators(
            symbol='BTC',
            timestamp=datetime.now(),
            rsi=65.5,
            macd={'macd': 100.5, 'signal': 95.2, 'histogram': 5.3}
        )
        
        result_dict = indicators.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['symbol'] == 'BTC'
        assert result_dict['rsi'] == 65.5
        assert result_dict['macd']['macd'] == 100.5
    
    def test_technical_indicators_get_signals(self):
        """测试交易信号生成"""
        # 测试超买信号
        indicators = TechnicalIndicators(
            symbol='BTC',
            timestamp=datetime.now(),
            rsi=75.0,  # 超买
            macd={'macd': 100.5, 'signal': 95.2, 'histogram': 5.3}  # 看涨
        )
        
        signals = indicators.get_signals()
        
        assert signals['rsi'] == 'overbought'
        assert signals['macd'] == 'bullish'
        
        # 测试超卖信号
        indicators.rsi = 25.0  # 超卖
        indicators.macd['histogram'] = -5.3  # 看跌
        
        signals = indicators.get_signals()
        
        assert signals['rsi'] == 'oversold'
        assert signals['macd'] == 'bearish'


class TestIndicatorAccuracy:
    """指标准确性测试"""
    
    def test_rsi_known_values(self):
        """使用已知数据测试RSI计算准确性"""
        # 使用简单的测试数据
        prices = [44, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.85, 46.08, 45.89,
                 46.03, 46.83, 47.69, 46.49, 46.26, 47.09, 46.66, 46.80, 46.23, 46.33]
        
        data = []
        for i, price in enumerate(prices):
            data.append({
                'timestamp': i,
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price,
                'volume': 1000
            })
        
        df = pd.DataFrame(data)
        analyzer = TechnicalAnalyzer()
        
        rsi = analyzer._calculate_rsi(df, {'rsi_period': 14})
        
        # RSI应该在合理范围内
        assert 30 <= rsi <= 70  # 对于这个相对稳定的价格序列
    
    def test_macd_crossover(self):
        """测试MACD交叉信号"""
        # 创建一个明显的趋势数据
        prices = list(range(100, 150))  # 上升趋势
        
        data = []
        for i, price in enumerate(prices):
            data.append({
                'timestamp': i,
                'open': price,
                'high': price * 1.01,
                'low': price * 0.99,
                'close': price,
                'volume': 1000
            })
        
        df = pd.DataFrame(data)
        analyzer = TechnicalAnalyzer()
        
        macd = analyzer._calculate_macd(df, {
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        })
        
        # 在上升趋势中，MACD线应该高于信号线
        assert macd['macd'] > macd['signal']
        assert macd['histogram'] > 0


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])