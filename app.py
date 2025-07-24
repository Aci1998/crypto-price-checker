from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

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
        'MATIC': 'MATIC/USDT'
    }
    
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
    
    # 尝试每个API源
    for source_name, api_func in api_sources:
        try:
            print(f"尝试 {source_name} API...")  # 调试信息
            data, error = api_func(symbol_pair)
            if data:
                print(f"✅ {source_name} API成功")  # 调试信息
                return data, None
            else:
                print(f"❌ {source_name} API失败: {error}")  # 调试信息
                all_errors.append(f"{source_name}: {error}")
                last_error = error
        except Exception as e:
            error_msg = f"{source_name} API异常: {str(e)}"
            print(f"❌ {error_msg}")  # 调试信息
            all_errors.append(error_msg)
            last_error = error_msg
            continue
    
    # 如果所有API都失败，返回详细的错误信息
    print(f"所有API都失败，错误列表: {all_errors}")  # 调试信息
    return None, f"网络异常：所有数据源暂时不可用。详细错误：{'; '.join(all_errors[:2])}"

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None
    
    if request.method == 'POST':
        coin_input = request.form.get('coin', '').strip()
        print(f"收到查询请求: '{coin_input}'")  # 调试信息
        
        if not coin_input:
            error = "请输入货币代码"
        else:
            # 标准化输入
            normalized_symbol = normalize_symbol(coin_input)
            print(f"标准化后的符号: '{normalized_symbol}'")  # 调试信息
            
            # 获取数据
            data, error = get_crypto_data(normalized_symbol)
            print(f"查询结果: data={bool(data)}, error={error}")  # 调试信息
    
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
    app.run(debug=True)