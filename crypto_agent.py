"""
加密货币查询Agent
支持自然语言查询加密货币价格信息
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List

class CryptoAgent:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # 本地API地址
        self.supported_currencies = [
            'BTC', 'ETH', 'ADA', 'DOT', 'LINK', 'LTC', 'XRP', 
            'BNB', 'SOL', 'MATIC', 'AVAX', 'DOGE', 'SHIB', 'UNI', 'ATOM'
        ]
        
    def extract_currency_from_text(self, text: str) -> Optional[str]:
        """从自然语言文本中提取货币代码"""
        text = text.upper()
        
        # 直接匹配货币代码
        for currency in self.supported_currencies:
            if currency in text:
                return currency
        
        # 匹配交易对格式
        pair_pattern = r'([A-Z]{2,10})[/\-]([A-Z]{2,10})'
        match = re.search(pair_pattern, text)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        
        # 匹配常见的货币名称（中英文）
        currency_names = {
            'BITCOIN': 'BTC',
            'ETHEREUM': 'ETH', 
            'CARDANO': 'ADA',
            'POLKADOT': 'DOT',
            'CHAINLINK': 'LINK',
            'LITECOIN': 'LTC',
            'RIPPLE': 'XRP',
            'BINANCE': 'BNB',
            'SOLANA': 'SOL',
            'POLYGON': 'MATIC',
            'AVALANCHE': 'AVAX',
            'DOGECOIN': 'DOGE',
            'SHIBA': 'SHIB',
            'UNISWAP': 'UNI',
            'COSMOS': 'ATOM',
            # 中文名称
            '比特币': 'BTC',
            '以太坊': 'ETH',
            '艾达币': 'ADA',
            '波卡': 'DOT',
            '链环': 'LINK',
            '莱特币': 'LTC',
            '瑞波币': 'XRP',
            '币安币': 'BNB',
            '索拉纳': 'SOL',
            '马蹄': 'MATIC',
            '雪崩': 'AVAX',
            '狗狗币': 'DOGE',
            '柴犬币': 'SHIB',
            '宇宙': 'ATOM',
            # 英文简写匹配
            'PRICE': None,  # 避免匹配到PRICE关键词
            'COIN': None,
            'TOKEN': None
        }
        
        for name, symbol in currency_names.items():
            if name in text and symbol:  # 确保symbol不为None
                return symbol
        
        # 如果包含常见关键词但没有具体币种，尝试提取第一个可能的代码
        if any(keyword in text for keyword in ['价格', 'PRICE', '多少钱', '查询', 'QUERY']):
            # 提取可能的3-4位字母组合
            matches = re.findall(r'\b[A-Z]{2,5}\b', text)
            for match in matches:
                if match in self.supported_currencies:
                    return match
                    
        return None
    
    def get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """获取加密货币价格信息"""
        try:
            response = requests.get(f"{self.base_url}/api/crypto/{symbol}", timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return {
                    'success': False,
                    'error': error_data.get('error', f'HTTP {response.status_code}')
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '无法连接到价格服务，请确保服务正在运行 (python app.py)'
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时，请稍后重试'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'查询失败: {str(e)}'
            }
    
    def format_price_response(self, data: Dict[str, Any]) -> str:
        """格式化价格响应为友好的文本"""
        if not data['success']:
            return f"❌ {data['error']}"
        
        info = data['data']
        
        # 判断涨跌
        change_emoji = "📈" if info['change_24h'] > 0 else "📉" if info['change_24h'] < 0 else "➡️"
        
        response = f"""
🪙 **{info['symbol']}** ({info['name']})

💰 **当前价格**: {info['price_formatted']}
{change_emoji} **24小时涨跌**: {info['change_formatted']}

📊 **24小时数据**:
   • 最高价: ${info['high_24h']:,.2f}
   • 最低价: ${info['low_24h']:,.2f}

📡 **数据源**: {info['source']}
🕐 **更新时间**: {info['last_updated']}
        """.strip()
        
        return response
    
    def process_query(self, query: str) -> str:
        """处理自然语言查询"""
        query = query.strip()
        
        # 提取货币代码
        currency = self.extract_currency_from_text(query)
        
        if not currency:
            return """
❓ 我没有识别出要查询的加密货币。

请尝试以下格式：
• "BTC价格" 或 "比特币价格"
• "查询ETH" 或 "以太坊多少钱"
• "BTC/USDT交易对"
• "告诉我SOL的价格"

支持的货币: BTC, ETH, ADA, SOL, BNB, DOGE 等
            """.strip()
        
        # 获取价格信息
        result = self.get_crypto_price(currency)
        return self.format_price_response(result)
    
    def get_multiple_prices(self, symbols: List[str]) -> str:
        """批量查询多个货币价格"""
        results = []
        
        for symbol in symbols:
            result = self.get_crypto_price(symbol)
            if result['success']:
                info = result['data']
                change_emoji = "📈" if info['change_24h'] > 0 else "📉" if info['change_24h'] < 0 else "➡️"
                results.append(f"{info['symbol']}: {info['price_formatted']} {change_emoji} {info['change_formatted']}")
            else:
                results.append(f"{symbol}: ❌ {result['error']}")
        
        return "🪙 **批量价格查询结果**:\n\n" + "\n".join(results)
    
    def get_market_overview(self) -> str:
        """获取市场概览"""
        major_coins = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL']
        return self.get_multiple_prices(major_coins)

# 创建全局agent实例
crypto_agent = CryptoAgent()

def query_crypto_price(query: str) -> str:
    """
    Agent函数：查询加密货币价格
    
    Args:
        query: 自然语言查询，如 "BTC价格", "比特币多少钱", "查询以太坊"
    
    Returns:
        格式化的价格信息字符串
    """
    return crypto_agent.process_query(query)

def get_crypto_market_overview() -> str:
    """
    Agent函数：获取主要加密货币市场概览
    
    Returns:
        主要货币的价格概览
    """
    return crypto_agent.get_market_overview()

def batch_query_crypto(symbols: str) -> str:
    """
    Agent函数：批量查询多个加密货币价格
    
    Args:
        symbols: 逗号分隔的货币代码，如 "BTC,ETH,ADA"
    
    Returns:
        批量查询结果
    """
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    return crypto_agent.get_multiple_prices(symbol_list)

# 命令行测试接口
if __name__ == "__main__":
    print("🤖 加密货币查询Agent启动")
    print("输入 'quit' 退出程序")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n💬 请输入查询: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 特殊命令处理
            if user_input.lower() in ['市场概览', 'market', 'overview']:
                response = get_crypto_market_overview()
            elif ',' in user_input and not any(word in user_input.lower() for word in ['价格', '多少', '查询']):
                # 批量查询格式：BTC,ETH,ADA
                response = batch_query_crypto(user_input)
            else:
                # 普通查询
                response = query_crypto_price(user_input)
            
            print(f"\n🤖 {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")