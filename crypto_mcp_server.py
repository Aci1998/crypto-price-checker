#!/usr/bin/env python3
"""
加密货币查询MCP服务器
用于Kiro IDE的Model Context Protocol集成
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from crypto_agent import crypto_agent

# MCP协议消息类型
class MCPMessage:
    def __init__(self, id: str, method: str, params: Dict[str, Any] = None):
        self.id = id
        self.method = method
        self.params = params or {}

class CryptoMCPServer:
    """加密货币查询MCP服务器"""
    
    def __init__(self):
        self.tools = {
            "query_crypto_price": {
                "description": "查询加密货币价格信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "自然语言查询或货币代码，如'BTC价格'、'比特币多少钱'、'BTC'等"
                        }
                    },
                    "required": ["query"]
                }
            },
            "get_market_overview": {
                "description": "获取主要加密货币市场概览",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "batch_query_crypto": {
                "description": "批量查询多个加密货币价格",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "string",
                            "description": "逗号分隔的货币代码，如'BTC,ETH,ADA'"
                        }
                    },
                    "required": ["symbols"]
                }
            }
        }
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "crypto-price-checker",
                "version": "1.0.0"
            }
        }
    
    async def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出可用工具"""
        tools = []
        for name, info in self.tools.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            })
        
        return {"tools": tools}
    
    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "query_crypto_price":
                query = arguments.get("query", "")
                result = crypto_agent.process_query(query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "get_market_overview":
                result = crypto_agent.get_market_overview()
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": result
                        }
                    ]
                }
            
            elif tool_name == "batch_query_crypto":
                symbols = arguments.get("symbols", "")
                symbol_list = [s.strip().upper() for s in symbols.split(',')]
                result = crypto_agent.get_multiple_prices(symbol_list)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ 未知工具: {tool_name}"
                        }
                    ],
                    "isError": True
                }
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ 工具执行错误: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP消息"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_list_tools(params)
            elif method == "tools/call":
                result = await self.handle_call_tool(params)
            else:
                result = {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            result = {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        
        response = {
            "jsonrpc": "2.0",
            "id": msg_id
        }
        
        if "error" in result:
            response["error"] = result["error"]
        else:
            response["result"] = result
        
        return response
    
    async def run(self):
        """运行MCP服务器"""
        print("加密货币查询MCP服务器启动", file=sys.stderr)
        print("等待MCP消息...", file=sys.stderr)
        
        while True:
            try:
                # 从stdin读取消息
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # 解析JSON消息
                try:
                    message = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析错误: {e}", file=sys.stderr)
                    continue
                
                # 处理消息
                response = await self.handle_message(message)
                
                # 发送响应
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 处理消息时出错: {e}", file=sys.stderr)

# 创建MCP配置文件
def create_mcp_config():
    """创建Kiro IDE的MCP配置"""
    config = {
        "mcpServers": {
            "crypto-price-checker": {
                "command": "python",
                "args": ["crypto_mcp_server.py"],
                "env": {},
                "disabled": False,
                "autoApprove": [
                    "query_crypto_price",
                    "get_market_overview", 
                    "batch_query_crypto"
                ]
            }
        }
    }
    
    with open("mcp_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("MCP配置文件已创建: mcp_config.json")
    print("\n使用说明:")
    print("1. 将mcp_config.json的内容添加到Kiro IDE的MCP配置中")
    print("2. 或者将配置复制到 ~/.kiro/settings/mcp.json")
    print("3. 重启Kiro IDE或重新连接MCP服务器")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        create_mcp_config()
    else:
        server = CryptoMCPServer()
        asyncio.run(server.run())