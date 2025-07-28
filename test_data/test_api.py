import requests
import time

def test_coingecko_api():
    """测试CoinGecko API连接"""
    print("正在测试CoinGecko API...")
    
    try:
        # 测试搜索API
        search_url = "https://api.coingecko.com/api/v3/search"
        print(f"测试搜索API: {search_url}")
        
        response = requests.get(search_url, params={'query': 'bitcoin'}, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            coins = data.get('coins', [])
            if coins:
                print(f"✅ 搜索API正常，找到 {len(coins)} 个结果")
                print(f"第一个结果: {coins[0]['id']} - {coins[0]['name']}")
                
                # 测试价格API
                coin_id = coins[0]['id']
                price_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
                print(f"\n测试价格API: {price_url}")
                
                price_response = requests.get(price_url, timeout=10)
                print(f"状态码: {price_response.status_code}")
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    market_data = price_data.get('market_data', {})
                    current_price = market_data.get('current_price', {})
                    usd_price = current_price.get('usd', 0)
                    
                    if usd_price > 0:
                        print(f"✅ 价格API正常，BTC价格: ${usd_price:,.2f}")
                        return True
                    else:
                        print("❌ 价格API返回数据异常")
                else:
                    print(f"❌ 价格API请求失败: {price_response.status_code}")
            else:
                print("❌ 搜索API返回空结果")
        else:
            print(f"❌ 搜索API请求失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
    
    return False

def test_alternative_apis():
    """测试备用API"""
    print("\n正在测试备用API...")
    
    # 测试OKX API
    try:
        print("测试OKX API...")
        okx_url = "https://www.okx.com/api/v5/market/ticker"
        response = requests.get(okx_url, params={'instId': 'BTC-USDT'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                price = float(data['data'][0]['last'])
                print(f"✅ OKX API正常，BTC/USDT价格: ${price:,.2f}")
                return True
            else:
                print(f"❌ OKX API返回错误: {data.get('msg', '未知错误')}")
        else:
            print(f"❌ OKX API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ OKX API错误: {str(e)}")
    
    # 测试Binance API
    try:
        print("测试Binance API...")
        binance_url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(binance_url, params={'symbol': 'BTCUSDT'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['lastPrice'])
            print(f"✅ Binance API正常，BTC/USDT价格: ${price:,.2f}")
            return True
        else:
            print(f"❌ Binance API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Binance API错误: {str(e)}")
    
    # 测试CoinCap API
    try:
        print("测试CoinCap API...")
        coincap_url = "https://api.coincap.io/v2/assets/bitcoin"
        response = requests.get(coincap_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data['data']['priceUsd'])
            print(f"✅ CoinCap API正常，BTC价格: ${price:,.2f}")
            return True
        else:
            print(f"❌ CoinCap API失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CoinCap API错误: {str(e)}")
    
    return False

def test_network_connectivity():
    """测试基本网络连接"""
    print("\n正在测试网络连接...")
    
    test_urls = [
        "https://www.google.com",
        "https://www.baidu.com",
        "https://httpbin.org/get"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} 连接正常")
                return True
        except Exception as e:
            print(f"❌ {url} 连接失败: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("=== API连接测试 ===")
    
    # 测试网络连接
    network_ok = test_network_connectivity()
    
    if network_ok:
        # 测试主要API
        coingecko_ok = test_coingecko_api()
        
        if not coingecko_ok:
            # 测试备用API
            alternative_ok = test_alternative_apis()
            
            if alternative_ok:
                print("\n✅ 备用API可用，建议切换到备用数据源")
            else:
                print("\n❌ 所有API都不可用")
        else:
            print("\n✅ 主要API正常工作")
    else:
        print("\n❌ 网络连接异常，请检查网络设置")