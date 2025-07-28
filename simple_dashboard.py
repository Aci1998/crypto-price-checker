#!/usr/bin/env python3
"""
简化版技术分析仪表板
使用Flask创建，不依赖外部HTTP库
"""

from flask import Flask, render_template_string, jsonify, request
import json
import sys
import os
from datetime import datetime
import asyncio

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

from technical_analysis import TechnicalAnalyzer

app = Flask(__name__)

# 创建技术分析器实例
analyzer = TechnicalAnalyzer()

# 简化的仪表板HTML模板
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币技术分析仪表板</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        
        .controls {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .control-group {
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        
        .control-group select, .control-group button {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .analyze-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        .analyze-btn:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        .analyze-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .indicator-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .indicator-name {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .indicator-value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .indicator-signal {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .signal-bullish { background: #28a745; color: white; }
        .signal-bearish { background: #dc3545; color: white; }
        .signal-neutral { background: #6c757d; color: white; }
        .signal-overbought { background: #fd7e14; color: white; }
        .signal-oversold { background: #20c997; color: white; }
        
        .details-section {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .details-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .details-table th, .details-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .details-table th {
            background: #e9ecef;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .hidden {
            display: none;
        }
        
        .performance-info {
            background: #e7f3ff;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .performance-info div {
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 加密货币技术分析仪表板</h1>
            <p>实时技术指标分析与交易信号</p>
        </div>
        
        <div class="controls">
            <div class="control-group">
                <label for="symbol">选择币种:</label>
                <select id="symbol">
                    <option value="BTC">Bitcoin (BTC)</option>
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="ADA">Cardano (ADA)</option>
                    <option value="DOT">Polkadot (DOT)</option>
                    <option value="LINK">Chainlink (LINK)</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="timeframe">时间框架:</label>
                <select id="timeframe">
                    <option value="1h">1小时</option>
                    <option value="4h">4小时</option>
                    <option value="1d">1天</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="period">历史周期:</label>
                <select id="period">
                    <option value="7d">7天</option>
                    <option value="30d" selected>30天</option>
                    <option value="90d">90天</option>
                </select>
            </div>
            
            <div class="control-group">
                <label>&nbsp;</label>
                <button id="analyzeBtn" class="analyze-btn" onclick="performAnalysis()">
                    📊 开始分析
                </button>
            </div>
        </div>
        
        <div id="errorMessage" class="error hidden"></div>
        <div id="loadingMessage" class="loading hidden">
            <h3>🔄 正在分析中...</h3>
            <p>请稍候，正在计算技术指标...</p>
        </div>
        
        <div id="resultsSection" class="hidden">
            <div class="indicators-grid" id="indicatorsGrid">
                <!-- 指标卡片将在这里动态生成 -->
            </div>
            
            <div class="details-section">
                <h3>📈 详细技术指标</h3>
                <table class="details-table" id="detailsTable">
                    <thead>
                        <tr>
                            <th>指标名称</th>
                            <th>当前值</th>
                            <th>交易信号</th>
                            <th>说明</th>
                        </tr>
                    </thead>
                    <tbody id="detailsTableBody">
                    </tbody>
                </table>
            </div>
            
            <div class="performance-info" id="performanceInfo">
                <!-- 性能信息将在这里显示 -->
            </div>
        </div>
    </div>

    <script>
        // 执行技术分析
        async function performAnalysis() {
            const symbol = document.getElementById('symbol').value;
            const timeframe = document.getElementById('timeframe').value;
            const period = document.getElementById('period').value;
            
            // 显示加载状态
            showLoading(true);
            hideError();
            hideResults();
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        symbol: symbol,
                        timeframe: timeframe,
                        period: period
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    showError(data.error || '分析失败');
                }
                
            } catch (error) {
                console.error('分析错误:', error);
                showError('网络错误或服务器异常: ' + error.message);
            } finally {
                showLoading(false);
            }
        }
        
        // 显示分析结果
        function displayResults(data) {
            // 生成指标卡片
            generateIndicatorCards(data.indicators, data.signals);
            
            // 生成详细表格
            generateDetailsTable(data.indicators, data.signals);
            
            // 显示性能信息
            displayPerformanceInfo(data);
            
            // 显示结果区域
            showResults();
        }
        
        // 生成指标卡片
        function generateIndicatorCards(indicators, signals) {
            const grid = document.getElementById('indicatorsGrid');
            grid.innerHTML = '';
            
            const cardData = [
                {
                    name: 'RSI (14)',
                    value: indicators.rsi,
                    signal: signals.rsi,
                    format: (v) => v ? v.toFixed(2) : '--'
                },
                {
                    name: 'MACD',
                    value: indicators.macd,
                    signal: signals.macd,
                    format: (v) => v ? v.histogram.toFixed(2) : '--'
                },
                {
                    name: 'SMA (20)',
                    value: indicators.sma_20,
                    signal: 'neutral',
                    format: (v) => v ? v.toFixed(2) : '--'
                },
                {
                    name: 'EMA (12)',
                    value: indicators.ema_12,
                    signal: 'neutral',
                    format: (v) => v ? v.toFixed(2) : '--'
                }
            ];
            
            cardData.forEach(card => {
                const cardElement = document.createElement('div');
                cardElement.className = 'indicator-card';
                cardElement.innerHTML = `
                    <div class="indicator-name">${card.name}</div>
                    <div class="indicator-value">${card.format(card.value)}</div>
                    <div class="indicator-signal signal-${card.signal}">${getSignalText(card.signal)}</div>
                `;
                grid.appendChild(cardElement);
            });
        }
        
        // 生成详细表格
        function generateDetailsTable(indicators, signals) {
            const tbody = document.getElementById('detailsTableBody');
            tbody.innerHTML = '';
            
            const tableData = [
                { name: 'RSI (14)', value: indicators.rsi, signal: signals.rsi, desc: '相对强弱指数，衡量超买超卖' },
                { name: 'MACD', value: indicators.macd, signal: signals.macd, desc: '移动平均收敛散度' },
                { name: 'SMA (20)', value: indicators.sma_20, signal: 'neutral', desc: '20期简单移动平均线' },
                { name: 'EMA (12)', value: indicators.ema_12, signal: 'neutral', desc: '12期指数移动平均线' },
                { name: 'Stochastic K', value: indicators.stochastic, signal: 'neutral', desc: '随机指标K值' },
                { name: 'Williams %R', value: indicators.williams_r, signal: 'neutral', desc: '威廉指标' },
                { name: 'CCI', value: indicators.cci, signal: 'neutral', desc: '商品通道指数' },
                { name: 'Momentum', value: indicators.momentum, signal: 'neutral', desc: '动量指标' }
            ];
            
            tableData.forEach(item => {
                if (item.value !== undefined && item.value !== null) {
                    const row = tbody.insertRow();
                    const formattedValue = typeof item.value === 'object' ? 
                        JSON.stringify(item.value) : 
                        (typeof item.value === 'number' ? item.value.toFixed(2) : item.value);
                    
                    row.innerHTML = `
                        <td>${item.name}</td>
                        <td>${formattedValue}</td>
                        <td><span class="indicator-signal signal-${item.signal}">${getSignalText(item.signal)}</span></td>
                        <td>${item.desc}</td>
                    `;
                }
            });
        }
        
        // 显示性能信息
        function displayPerformanceInfo(data) {
            const perfInfo = document.getElementById('performanceInfo');
            perfInfo.innerHTML = `
                <h4>⚡ 性能信息</h4>
                <div><strong>币种:</strong> ${data.symbol}</div>
                <div><strong>时间框架:</strong> ${data.timeframe}</div>
                <div><strong>数据点数:</strong> ${data.data_points_used}</div>
                <div><strong>计算耗时:</strong> ${data.calculation_time_ms.toFixed(2)}ms</div>
                <div><strong>分析时间:</strong> ${new Date(data.timestamp).toLocaleString()}</div>
            `;
        }
        
        // 获取信号文本
        function getSignalText(signal) {
            const signalMap = {
                'bullish': '看涨',
                'bearish': '看跌',
                'overbought': '超买',
                'oversold': '超卖',
                'neutral': '中性'
            };
            return signalMap[signal] || '中性';
        }
        
        // 显示/隐藏函数
        function showLoading(show) {
            const loading = document.getElementById('loadingMessage');
            const btn = document.getElementById('analyzeBtn');
            
            if (show) {
                loading.classList.remove('hidden');
                btn.disabled = true;
                btn.textContent = '🔄 分析中...';
            } else {
                loading.classList.add('hidden');
                btn.disabled = false;
                btn.textContent = '📊 开始分析';
            }
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = '❌ ' + message;
            errorDiv.classList.remove('hidden');
        }
        
        function hideError() {
            document.getElementById('errorMessage').classList.add('hidden');
        }
        
        function showResults() {
            document.getElementById('resultsSection').classList.remove('hidden');
        }
        
        function hideResults() {
            document.getElementById('resultsSection').classList.add('hidden');
        }
        
        // 页面加载完成后自动执行一次分析
        window.onload = function() {
            performAnalysis();
        };
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """主页"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """技术分析API"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC')
        timeframe = data.get('timeframe', '1h')
        period = data.get('period', '30d')
        
        # 使用asyncio运行异步分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                analyzer.analyze(
                    symbol=symbol,
                    timeframe=timeframe,
                    period=period
                )
            )
        finally:
            loop.close()
        
        # 构建响应数据
        indicators = {}
        if result.rsi is not None:
            indicators['rsi'] = result.rsi
        if result.macd is not None:
            indicators['macd'] = result.macd
        if result.bollinger_bands is not None:
            indicators['bollinger_bands'] = result.bollinger_bands
        if result.sma_20 is not None:
            indicators['sma_20'] = result.sma_20
        if result.sma_50 is not None:
            indicators['sma_50'] = result.sma_50
        if result.ema_12 is not None:
            indicators['ema_12'] = result.ema_12
        if result.ema_26 is not None:
            indicators['ema_26'] = result.ema_26
        if result.stochastic is not None:
            indicators['stochastic'] = result.stochastic
        if result.williams_r is not None:
            indicators['williams_r'] = result.williams_r
        if result.cci is not None:
            indicators['cci'] = result.cci
        if result.momentum is not None:
            indicators['momentum'] = result.momentum
        
        return jsonify({
            'success': True,
            'symbol': result.symbol,
            'timeframe': result.timeframe,
            'timestamp': result.timestamp.isoformat(),
            'data_points_used': result.data_points_used,
            'calculation_time_ms': result.calculation_time_ms or 0,
            'indicators': indicators,
            'signals': result.get_signals()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动简化版技术分析仪表板...")
    print("📊 访问地址: http://localhost:5000")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )