"""
加密货币查询Agent集成示例
支持多种Agent框架的集成方式
"""

import json
from typing import Dict, Any, List
from crypto_agent import crypto_agent

# ==================== LangChain集成 ====================

def create_langchain_tool():
    """创建LangChain工具"""
    try:
        from langchain.tools import Tool
        from langchain.agents import initialize_agent, AgentType
        from langchain.llms import OpenAI
        
        def crypto_price_tool(query: str) -> str:
            """LangChain工具函数"""
            return crypto_agent.process_query(query)
        
        crypto_tool = Tool(
            name="CryptoPriceChecker",
            description="查询加密货币价格信息。输入货币代码或自然语言查询，如'BTC价格'、'比特币多少钱'等",
            func=crypto_price_tool
        )
        
        return crypto_tool
        
    except ImportError:
        print("❌ LangChain未安装，请运行: pip install langchain")
        return None

def langchain_example():
    """LangChain使用示例"""
    tool = create_langchain_tool()
    if tool:
        # 使用示例
        result = tool.run("BTC价格")
        print("LangChain结果:", result)

# ==================== OpenAI Function Calling集成 ====================

def get_openai_function_schema():
    """获取OpenAI Function Calling的schema"""
    return {
        "name": "query_crypto_price",
        "description": "查询加密货币的实时价格信息",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "加密货币代码，如BTC、ETH、ADA等"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["price", "overview", "batch"],
                    "description": "查询类型：price(单个价格)、overview(市场概览)、batch(批量查询)"
                }
            },
            "required": ["symbol"]
        }
    }

def handle_openai_function_call(function_call: Dict[str, Any]) -> str:
    """处理OpenAI Function Calling"""
    try:
        args = json.loads(function_call.get("arguments", "{}"))
        symbol = args.get("symbol", "")
        query_type = args.get("query_type", "price")
        
        if query_type == "overview":
            return crypto_agent.get_market_overview()
        elif query_type == "batch":
            symbols = symbol.split(",")
            return crypto_agent.get_multiple_prices(symbols)
        else:
            return crypto_agent.process_query(symbol)
            
    except Exception as e:
        return f"❌ 处理函数调用时出错: {str(e)}"

# ==================== 自定义Agent框架集成 ====================

class CryptoAgentPlugin:
    """自定义Agent插件"""
    
    def __init__(self):
        self.name = "crypto_price_checker"
        self.description = "加密货币价格查询插件"
        self.version = "1.0.0"
        
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """获取插件能力"""
        return [
            {
                "name": "query_price",
                "description": "查询单个加密货币价格",
                "parameters": ["symbol"],
                "example": "query_price('BTC')"
            },
            {
                "name": "market_overview", 
                "description": "获取主要加密货币市场概览",
                "parameters": [],
                "example": "market_overview()"
            },
            {
                "name": "batch_query",
                "description": "批量查询多个加密货币价格", 
                "parameters": ["symbols"],
                "example": "batch_query(['BTC', 'ETH', 'ADA'])"
            }
        ]
    
    def execute(self, action: str, **kwargs) -> str:
        """执行插件动作"""
        if action == "query_price":
            symbol = kwargs.get("symbol", "")
            return crypto_agent.process_query(symbol)
            
        elif action == "market_overview":
            return crypto_agent.get_market_overview()
            
        elif action == "batch_query":
            symbols = kwargs.get("symbols", [])
            return crypto_agent.get_multiple_prices(symbols)
            
        else:
            return f"❌ 未知动作: {action}"

# ==================== REST API Agent集成 ====================

def create_agent_api_endpoints():
    """创建Agent API端点"""
    from flask import Flask, request, jsonify
    
    agent_app = Flask(__name__)
    
    @agent_app.route('/agent/crypto/query', methods=['POST'])
    def agent_crypto_query():
        """Agent查询端点"""
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': '查询内容不能为空'}), 400
        
        result = crypto_agent.process_query(query)
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': crypto_agent.get_crypto_price('BTC')['data']['last_updated'] if crypto_agent.get_crypto_price('BTC')['success'] else None
        })
    
    @agent_app.route('/agent/crypto/overview', methods=['GET'])
    def agent_crypto_overview():
        """市场概览端点"""
        result = crypto_agent.get_market_overview()
        return jsonify({
            'success': True,
            'result': result
        })
    
    @agent_app.route('/agent/crypto/batch', methods=['POST'])
    def agent_crypto_batch():
        """批量查询端点"""
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': '货币代码列表不能为空'}), 400
        
        result = crypto_agent.get_multiple_prices(symbols)
        return jsonify({
            'success': True,
            'result': result
        })
    
    return agent_app

# ==================== Webhook集成 ====================

def create_webhook_handler():
    """创建Webhook处理器"""
    def handle_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理Webhook请求"""
        try:
            message_type = data.get('type', '')
            content = data.get('content', '')
            
            if message_type == 'crypto_query':
                result = crypto_agent.process_query(content)
                return {
                    'success': True,
                    'response': result,
                    'type': 'crypto_response'
                }
            
            elif message_type == 'crypto_overview':
                result = crypto_agent.get_market_overview()
                return {
                    'success': True,
                    'response': result,
                    'type': 'crypto_overview'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'未支持的消息类型: {message_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'处理Webhook时出错: {str(e)}'
            }
    
    return handle_webhook

# ==================== 使用示例 ====================

def demo_integrations():
    """演示各种集成方式"""
    print("🚀 加密货币Agent集成演示")
    print("=" * 50)
    
    # 1. 直接使用
    print("\n1️⃣ 直接使用:")
    result = crypto_agent.process_query("BTC价格")
    print(result)
    
    # 2. 自定义插件
    print("\n2️⃣ 自定义插件:")
    plugin = CryptoAgentPlugin()
    result = plugin.execute("query_price", symbol="ETH")
    print(result)
    
    # 3. OpenAI Function Calling模拟
    print("\n3️⃣ OpenAI Function Calling模拟:")
    function_call = {
        "arguments": json.dumps({"symbol": "ADA", "query_type": "price"})
    }
    result = handle_openai_function_call(function_call)
    print(result)
    
    # 4. Webhook模拟
    print("\n4️⃣ Webhook模拟:")
    webhook_handler = create_webhook_handler()
    webhook_data = {
        "type": "crypto_query",
        "content": "SOL价格"
    }
    result = webhook_handler(webhook_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    demo_integrations()