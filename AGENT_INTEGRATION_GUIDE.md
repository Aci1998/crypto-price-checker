# 🤖 Agent集成指南

本指南介绍如何将加密货币查询API集成到各种Agent系统中。

## 📋 集成方式概览

| 集成方式 | 文件 | 适用场景 |
|---------|------|----------|
| 直接调用 | `crypto_agent.py` | 简单脚本、命令行工具 |
| MCP协议 | `crypto_mcp_server.py` | Kiro IDE、Claude Desktop |
| LangChain | `agent_integrations.py` | LangChain应用 |
| OpenAI Functions | `agent_integrations.py` | GPT应用 |
| REST API | `agent_integrations.py` | Web服务、微服务 |
| Webhook | `agent_integrations.py` | 聊天机器人、通知系统 |

## 🚀 快速开始

### 1. 启动价格服务
```bash
# 启动Flask API服务
python app.py
```

### 2. 测试Agent功能
```bash
# 测试基础Agent
python crypto_agent.py

# 测试集成示例
python agent_integrations.py
```

## 🔧 Kiro IDE集成 (推荐)

### 方法1: MCP服务器集成

1. **生成MCP配置**:
```bash
python crypto_mcp_server.py config
```

2. **添加到Kiro配置**:
将生成的配置添加到 `~/.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "crypto-price-checker": {
      "command": "python",
      "args": ["crypto_mcp_server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": [
        "query_crypto_price",
        "get_market_overview",
        "batch_query_crypto"
      ]
    }
  }
}
```

3. **在Kiro中使用**:
```
用户: 查询BTC价格
Kiro: [调用 query_crypto_price 工具]
```

### 方法2: 直接集成

将 `crypto_agent.py` 中的函数直接集成到你的Agent代码中:

```python
from crypto_agent import query_crypto_price, get_crypto_market_overview

# 在你的Agent中使用
def handle_crypto_query(user_input):
    if "价格" in user_input or "多少钱" in user_input:
        return query_crypto_price(user_input)
    elif "市场" in user_input or "概览" in user_input:
        return get_crypto_market_overview()
```

## 💬 自然语言支持

Agent支持多种自然语言查询格式:

### 支持的查询格式
- `"BTC价格"` → 查询比特币价格
- `"比特币多少钱"` → 查询比特币价格  
- `"查询以太坊"` → 查询以太坊价格
- `"ETH/USDT交易对"` → 查询ETH/USDT价格
- `"告诉我SOL的价格"` → 查询Solana价格
- `"市场概览"` → 获取主要币种概览
- `"BTC,ETH,ADA"` → 批量查询多个币种

### 支持的货币
BTC, ETH, ADA, DOT, LINK, LTC, XRP, BNB, SOL, MATIC, AVAX, DOGE, SHIB, UNI, ATOM

## 🔌 其他框架集成

### LangChain集成
```python
from agent_integrations import create_langchain_tool

# 创建工具
crypto_tool = create_langchain_tool()

# 添加到Agent
tools = [crypto_tool]
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
```

### OpenAI Function Calling
```python
from agent_integrations import get_openai_function_schema, handle_openai_function_call

# 获取函数schema
function_schema = get_openai_function_schema()

# 在OpenAI API调用中使用
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    functions=[function_schema]
)
```

### REST API集成
```python
from agent_integrations import create_agent_api_endpoints

# 创建Flask应用
agent_app = create_agent_api_endpoints()

# 启动API服务
agent_app.run(port=5001)
```

API端点:
- `POST /agent/crypto/query` - 自然语言查询
- `GET /agent/crypto/overview` - 市场概览
- `POST /agent/crypto/batch` - 批量查询

## 🧪 测试和调试

### 1. 测试API连接
```bash
python test_api.py
```

### 2. 测试Agent功能
```bash
# 交互式测试
python crypto_agent.py

# 输入示例:
# > BTC价格
# > 比特币多少钱
# > 市场概览
# > BTC,ETH,ADA
```

### 3. 测试MCP服务器
```bash
# 启动MCP服务器
python crypto_mcp_server.py

# 发送测试消息 (JSON格式)
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
```

## 🔧 自定义配置

### 修改API地址
在 `crypto_agent.py` 中修改:
```python
self.base_url = "http://your-api-server:5000"
```

### 添加新货币
在 `normalize_symbol` 函数中添加:
```python
common_pairs = {
    'BTC': 'BTC/USDT',
    'YOUR_COIN': 'YOUR_COIN/USDT',  # 添加新币种
    # ...
}
```

### 自定义响应格式
修改 `format_price_response` 函数来自定义输出格式。

## 🚨 故障排除

### 常见问题

1. **连接错误**
   - 确保Flask API服务正在运行 (`python app.py`)
   - 检查端口是否被占用

2. **MCP服务器无响应**
   - 检查Python路径是否正确
   - 确保所有依赖已安装

3. **查询失败**
   - 检查网络连接
   - 验证货币代码是否正确
   - 查看API服务日志

### 调试模式
设置环境变量启用调试:
```bash
export FLASK_ENV=development
python app.py
```

## 📈 性能优化

1. **缓存机制**: 添加Redis缓存减少API调用
2. **连接池**: 使用requests.Session()复用连接
3. **异步处理**: 使用asyncio处理并发请求
4. **限流**: 添加请求频率限制

## 🔐 安全建议

1. 不要在生产环境暴露调试信息
2. 添加API密钥验证
3. 实现请求频率限制
4. 使用HTTPS传输数据

## 📚 扩展功能

可以基于现有框架扩展的功能:
- 价格预警通知
- 历史价格查询
- 技术指标计算
- 投资组合跟踪
- 新闻情感分析

---

如有问题，请查看项目的Issue页面或联系维护者。