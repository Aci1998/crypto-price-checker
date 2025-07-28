# 虚拟货币查询工具

一个简洁美观的加密货币价格查询工具，支持实时获取多种数字货币的价格信息。

## ✨ 功能特性

- 🔍 **智能搜索**：支持多种输入格式（BTC、BTC/USDT、btc等）
- 📊 **实时数据**：显示当前价格、24小时涨跌幅、最高最低价
- 🌐 **多数据源**：支持OKX、Binance、CoinGecko等多个API源，自动切换
- 💡 **智能错误处理**：友好的错误提示，区分网络异常和无效输入
- 🎨 **现代化界面**：响应式设计，美观的卡片展示
- ⚡ **快速响应**：优化的API调用，快速获取数据

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Flask 2.3.3+
- requests 2.31.0+

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/你的用户名/crypto-price-checker.git
cd crypto-price-checker
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python app.py
```

4. 打开浏览器访问 `http://localhost:5000`

## 📱 使用方法

1. 在搜索框中输入加密货币代码
2. 支持的输入格式：
   - `BTC` - 自动转换为 BTC/USDT
   - `BTC/USDT` - 完整交易对
   - `eth` - 大小写不敏感
   - `ADA/BTC` - 自定义交易对

3. 点击查询按钮获取实时价格信息
<img width="2174" height="1276" alt="图片" src="https://github.com/user-attachments/assets/6ec29312-5b24-4fc9-b8d2-1a96ce57deb7" />

## 🛠️ 技术栈

- **后端**：Flask (Python)
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **数据源**：OKX API, Binance API, CoinGecko API
- **图标**：Font Awesome

## 📊 支持的数据源

| 数据源 | 优先级 | 特点 |
|--------|--------|------|
| OKX | 1 | 快速响应，数据准确 |
| Binance | 2 | 全球最大交易所，数据可靠 |
| CoinGecko | 3 | 币种覆盖广，备用数据源 |

## 🎯 支持的加密货币

常见币种包括但不限于：
- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)
- Solana (SOL)
- Binance Coin (BNB)
- Chainlink (LINK)
- Polygon (MATIC)
- 以及更多...

## 🔧 API接口

项目还提供了RESTful API接口：

```
GET /api/crypto/<symbol>
```

示例：
```bash
curl http://localhost:5000/api/crypto/BTC
```

## 📝 项目结构

```
crypto-price-checker/
├── app.py              # Flask应用主文件
├── requirements.txt    # Python依赖
├── templates/
│   └── index.html     # 前端模板
├── test_api.py        # API测试脚本
├── test_crypto.py     # 功能测试脚本
└── README.md          # 项目说明
```

## 🧪 测试

运行API连接测试：
```bash
python test_api.py
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [CoinGecko](https://www.coingecko.com/) - 提供加密货币数据API
- [Binance](https://binance.com/) - 提供交易数据API
- [OKX](https://www.okx.com/) - 提供实时价格数据
- [Bootstrap](https://getbootstrap.com/) - 前端UI框架
- [Font Awesome](https://fontawesome.com/) - 图标库

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](https://github.com/你的用户名/crypto-price-checker/issues)
- 发送邮件至：imacaiy@outlook.com

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
