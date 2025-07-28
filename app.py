from flask import Flask, render_template, request, jsonify
import requests
import os
import sys
import asyncio
from datetime import datetime

# 添加enhanced目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'enhanced'))

# 导入技术分析模块
try:
    from technical_analysis import TechnicalAnalyzer
    TECHNICAL_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"技术分析模块导入失败: {e}")
    TECHNICAL_ANALYSIS_AVAILABLE = False

app = Flask(__name__)

# 生产环境配置
DEBUG_MODE = os.environ.get('FLASK_ENV') != 'production'

# 创建技术分析器实例
if TECHNICAL_ANALYSIS_AVAILABLE:
    technical_analyzer = TechnicalAnalyzer()
else:
    technical_analyzer = None

def normalize_symbol(input_symbol):
    """标准化货币代码输入"""
    input_symbol = input_symbol.strip().upper()
    
    # 常见交易对映射
    common_pairs = {
        'BTC': 'BTC/USDT',
        'ETH': 'ETH/USDT', 
        'ADA': 'ADA/USDT',
        'DOT': 'DOT/USDT',
        'LINK': 'LINK/USDT',
        'LTC': 'LTC/USDT',
        'XRP': 'XRP/USDT',
        'BNB': 'BNB/USDT',
        'SOL': 'SOL/USDT',
        'MATIC': 'MATIC/USDT',
        'AVAX': 'AVAX/USDT',
        'DOGE': 'DOGE/USDT',
        'SHIB': 'SHIB/USDT',
        'UNI': 'UNI/USDT',
        'ATOM': 'ATOM/USDT'
    }
    
    # 无效输入检查
    invalid_inputs = ['OKX', 'BINANCE', 'HUOBI', 'COINBASE', 'KRAKEN']
    if input_symbol in invalid_inputs:
        return None  # 返回None表示无效输入
    
    # 如果输入已经是交易对格式，直接返回
    if '/' in input_symbol:
        return input_symbol
    
    # 如果是常见币种，返回对应的USDT交易对
    if input_symbol in common_pairs:
        return common_pairs[input_symbol]
    
    # 默认添加/USDT
    return f"{input_symbol}/USDT"

def get_crypto_data_okx(symbol_pair):
    """使用OKX API获取数据"""
    try:
        base_symbol = symbol_pair.split('/')[0]
        quote_symbol = symbol_pair.split('/')[1] if '/' in symbol_pair else 'USDT'
        
        # OKX API格式：BTC-USDT
        okx_symbol = f"{base_symbol}-{quote_symbol}"
        
        # 获取24小时价格统计
        ticker_url = "https://www.okx.com/api/v5/market/ticker"
        response = requests.get(ticker_url, params={'instId': okx_symbol}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                ticker_data = data['data'][0]
                price = float(ticker_data['last'])
                open_24h = float(ticker_data['open24h'])
                # 计算24小时涨跌幅
                change_24h = ((price - open_24h) / open_24h) * 100
                
                return {
                    'symbol': symbol_pair,
                    'name': base_symbol,
                    'price': price,
                    'price_formatted': f"${price:,.2f}" if quote_symbol in ['USDT', 'USD'] else f"{price:,.6f} {quote_symbol}",
                    'change_24h': change_24h,
                    'change_formatted': f"{change_24h:+.2f}%",
                    'quote_currency': quote_symbol,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'high_24h': float(ticker_data['high24h']),
                    'low_24h': float(ticker_data['low24h']),
                    'volume': float(ticker_data['vol24h']),
                    'source': 'OKX'
                }, None
        
        return None, f"OKX API: 未找到交易对 {okx_symbol}"
        
    except Exception as e:
        return None, f"OKX API错误: {str(e)}"

def get_crypto_data_binance(symbol_pair):
    """使用Binance API获取数据"""
    try:
        base_symbol = symbol_pair.split('/')[0]
        quote_symbol = symbol_pair.split('/')[1] if '/' in symbol_pair else 'USDT'
        
        # Binance API格式：BTCUSDT
        binance_symbol = f"{base_symbol}{quote_symbol}"
        
        # 获取24小时价格统计
        ticker_url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(ticker_url, params={'symbol': binance_symbol}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['lastPrice'])
            change_percent = float(data['priceChangePercent'])
            
            return {
                'symbol': symbol_pair,
                'name': base_symbol,
                'price': price,
                'price_formatted': f"${price:,.2f}" if quote_symbol in ['USDT', 'USD'] else f"{price:,.6f} {quote_symbol}",
                'change_24h': change_percent,
                'change_formatted': f"{change_percent:+.2f}%",
                'quote_currency': quote_symbol,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume': float(data['volume']),
                'source': 'Binance'
            }, None
        
        return None, f"Binance API: 未找到交易对 {binance_symbol}"
        
    except Exception as e:
        return None, f"Binance API错误: {str(e)}"

def get_crypto_data_coingecko(symbol_pair):
    """使用CoinGecko API获取数据"""
    try:
        base_symbol = symbol_pair.split('/')[0]
        quote_symbol = symbol_pair.split('/')[1] if '/' in symbol_pair else 'USDT'
        
        # 使用CoinGecko API搜索币种
        search_url = "https://api.coingecko.com/api/v3/search"
        search_response = requests.get(search_url, params={'query': base_symbol}, timeout=10)
        search_response.raise_for_status()
        search_results = search_response.json().get('coins', [])
        
        if not search_results:
            return None, f"CoinGecko: 未找到 '{base_symbol}' 相关的加密货币"
        
        coin_id = search_results[0]['id']
        coin_name = search_results[0]['name']
        
        # 获取详细价格数据
        price_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        price_response = requests.get(price_url, timeout=10)
        price_response.raise_for_status()
        coin_data = price_response.json()
        
        market_data = coin_data.get('market_data', {})
        if not market_data:
            return None, "CoinGecko: 无法获取市场数据"
        
        current_price = market_data.get('current_price', {})
        price_change_24h = market_data.get('price_change_percentage_24h', 0)
        
        # 根据报价货币选择价格
        quote_currency = quote_symbol.lower()
        if quote_currency == 'usdt':
            quote_currency = 'usd'  # CoinGecko使用USD而不是USDT
        
        price = current_price.get(quote_currency, current_price.get('usd', 0))
        
        if price == 0:
            return None, f"CoinGecko: 无法获取 {symbol_pair} 的价格信息"
        
        return {
            'symbol': symbol_pair,
            'name': coin_name,
            'price': price,
            'price_formatted': f"${price:,.2f}" if quote_currency in ['usd', 'usdt'] else f"{price:,.6f} {quote_symbol}",
            'change_24h': price_change_24h,
            'change_formatted': f"{price_change_24h:+.2f}%",
            'quote_currency': quote_symbol,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'high_24h': market_data.get('high_24h', {}).get(quote_currency, 0),
            'low_24h': market_data.get('low_24h', {}).get(quote_currency, 0),
            'market_cap': market_data.get('market_cap', {}).get(quote_currency, 0),
            'source': 'CoinGecko'
        }, None
        
    except Exception as e:
        return None, f"CoinGecko API错误: {str(e)}"

def get_crypto_data(symbol_pair):
    """获取加密货币数据，使用多个API源"""
    
    # API源列表，按优先级排序
    api_sources = [
        ("OKX", get_crypto_data_okx),
        ("Binance", get_crypto_data_binance),
        ("CoinGecko", get_crypto_data_coingecko),
    ]
    
    last_error = None
    all_errors = []
    
    not_found_count = 0  # 统计"未找到"错误的数量
    
    # 尝试每个API源
    for source_name, api_func in api_sources:
        try:
            if DEBUG_MODE:
                print(f"尝试 {source_name} API...")  # 调试信息
            data, error = api_func(symbol_pair)
            if data:
                if DEBUG_MODE:
                    print(f"✅ {source_name} API成功")  # 调试信息
                return data, None
            else:
                if DEBUG_MODE:
                    print(f"❌ {source_name} API失败: {error}")  # 调试信息
                all_errors.append(f"{source_name}: {error}")
                
                # 检查是否是"未找到交易对"的错误
                if "未找到交易对" in error or "未找到" in error:
                    not_found_count += 1
                
                last_error = error
        except Exception as e:
            error_msg = f"{source_name} API异常: {str(e)}"
            if DEBUG_MODE:
                print(f"❌ {error_msg}")  # 调试信息
            all_errors.append(error_msg)
            last_error = error_msg
            continue
    
    # 分析错误类型并返回合适的错误信息
    if DEBUG_MODE:
        print(f"所有API都失败，错误列表: {all_errors}")  # 调试信息
    
    base_symbol = symbol_pair.split('/')[0]
    
    # 如果大部分API都返回"未找到"错误，说明是无效的货币代码
    if not_found_count >= 2:
        return None, f"抱歉，没有找到 '{base_symbol}' 相关的加密货币。请检查货币代码是否正确，或尝试使用其他常见币种如 BTC、ETH、ADA 等。"
    
    # 如果是网络相关错误
    network_errors = ["timeout", "连接", "网络", "Connection", "Max retries"]
    has_network_error = any(any(net_err in error for net_err in network_errors) for error in all_errors)
    
    if has_network_error:
        return None, "网络异常：连接不稳定，请检查网络连接后重试。"
    
    # 其他错误
    return None, f"数据获取失败：{last_error}"

def get_technical_analysis(symbol, current_price=None):
    """获取技术分析数据"""
    if not TECHNICAL_ANALYSIS_AVAILABLE or not technical_analyzer:
        return None
    
    try:
        # 标准化符号格式
        base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
        
        # 使用asyncio运行异步分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                technical_analyzer.analyze(
                    symbol=base_symbol,
                    timeframe='1h',
                    period='30d',
                    current_price=current_price
                )
            )
            
            # 构建技术分析数据
            technical_data = {
                'rsi': result.rsi,
                'macd': result.macd,
                'bollinger_bands': result.bollinger_bands,
                'sma_20': result.sma_20,
                'sma_50': result.sma_50,
                'ema_12': result.ema_12,
                'ema_26': result.ema_26,
                'stochastic': result.stochastic,
                'williams_r': result.williams_r,
                'cci': result.cci,
                'momentum': result.momentum,
                'signals': result.get_signals(),
                'calculation_time_ms': result.calculation_time_ms,
                'data_points_used': result.data_points_used
            }
            
            return technical_data
            
        finally:
            loop.close()
            
    except Exception as e:
        if DEBUG_MODE:
            print(f"技术分析失败: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None
    
    if request.method == 'POST':
        coin_input = request.form.get('coin', '').strip()
        if DEBUG_MODE:
            print(f"收到查询请求: '{coin_input}'")  # 调试信息
        
        if not coin_input:
            error = "请输入货币代码"
        else:
            # 标准化输入
            normalized_symbol = normalize_symbol(coin_input)
            if DEBUG_MODE:
                print(f"标准化后的符号: '{normalized_symbol}'")  # 调试信息
            
            if normalized_symbol is None:
                error = f"'{coin_input}' 不是有效的加密货币代码。请尝试输入如 BTC、ETH、ADA 等常见币种。"
            else:
                # 获取数据
                data, error = get_crypto_data(normalized_symbol)
                if DEBUG_MODE:
                    print(f"查询结果: data={bool(data)}, error={error}")  # 调试信息
                
                # 如果成功获取价格数据，尝试获取技术分析数据
                if data and not error:
                    # 传入当前价格用于生成更准确的模拟数据
                    current_price = data.get('price', None)
                    technical_data = get_technical_analysis(normalized_symbol, current_price)
                    if technical_data:
                        data['technical_analysis'] = technical_data
                        if DEBUG_MODE:
                            print("✅ 技术分析数据已添加")
    
    return render_template('index.html', data=data, error=error)

@app.route('/api/crypto/<symbol>')
def api_crypto(symbol):
    """API接口，返回JSON数据"""
    normalized_symbol = normalize_symbol(symbol)
    data, error = get_crypto_data(normalized_symbol)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(data)

if __name__ == '__main__':
    # 支持Heroku等云平台的端口配置
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)