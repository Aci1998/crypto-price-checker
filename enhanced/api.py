#!/usr/bin/env python3
"""
FastAPI接口模块
提供技术分析的REST API接口
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

try:
    from .technical_analysis import TechnicalAnalyzer, IndicatorType
    from .historical_data import HistoricalDataManager
    from .config import config
except ImportError:
    from technical_analysis import TechnicalAnalyzer, IndicatorType
    from historical_data import HistoricalDataManager
    from config import config

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Enhanced Crypto Agent API",
    description="加密货币技术分析API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 全局实例
technical_analyzer = TechnicalAnalyzer()
historical_data_manager = HistoricalDataManager()

# 请求/响应模型
class TechnicalAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="币种代码，如BTC、ETH")
    indicators: Optional[List[str]] = Field(None, description="要计算的指标列表")
    timeframe: str = Field("1h", description="时间框架")
    period: str = Field("30d", description="历史数据周期")

class TechnicalAnalysisResponse(BaseModel):
    success: bool
    symbol: str
    timeframe: str
    timestamp: str
    data_points_used: int
    calculation_time_ms: float
    indicators: Dict[str, Any]
    signals: Dict[str, str]
    error: Optional[str] = None

class HistoricalDataResponse(BaseModel):
    success: bool
    symbol: str
    timeframe: str
    data_count: int
    data: List[Dict[str, Any]]
    error: Optional[str] = None

class SupportedSymbolsResponse(BaseModel):
    success: bool
    symbols: List[Dict[str, Any]]

# API路由
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Crypto Agent</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; margin-bottom: 30px; }
            .nav { text-align: center; margin-bottom: 30px; }
            .nav a { margin: 0 15px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #0056b3; }
            .feature { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .feature h3 { color: #007bff; margin-top: 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Enhanced Crypto Agent</h1>
            <div class="nav">
                <a href="/dashboard">📊 技术分析仪表板</a>
                <a href="/docs">📚 API文档</a>
                <a href="/api/v1/symbols">🔗 支持的币种</a>
            </div>
            
            <div class="feature">
                <h3>📈 技术分析功能</h3>
                <p>支持多种技术指标计算：RSI、MACD、布林带、移动平均线等</p>
                <p>实时计算，响应时间小于3秒</p>
            </div>
            
            <div class="feature">
                <h3>📊 数据可视化</h3>
                <p>交互式图表展示价格走势和技术指标</p>
                <p>支持多时间框架分析</p>
            </div>
            
            <div class="feature">
                <h3>🔔 交易信号</h3>
                <p>基于技术指标自动生成买卖信号</p>
                <p>支持自定义信号策略</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """技术分析仪表板页面"""
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/v1/symbols", response_model=SupportedSymbolsResponse)
async def get_supported_symbols():
    """获取支持的币种列表"""
    try:
        # 这里可以从数据库或配置中获取支持的币种
        symbols = [
            {"symbol": "BTC", "name": "Bitcoin", "supports_technical_analysis": True},
            {"symbol": "ETH", "name": "Ethereum", "supports_technical_analysis": True},
            {"symbol": "ADA", "name": "Cardano", "supports_technical_analysis": True},
            {"symbol": "DOT", "name": "Polkadot", "supports_technical_analysis": True},
            {"symbol": "LINK", "name": "Chainlink", "supports_technical_analysis": True},
            {"symbol": "LTC", "name": "Litecoin", "supports_technical_analysis": True},
            {"symbol": "XRP", "name": "Ripple", "supports_technical_analysis": True},
            {"symbol": "BNB", "name": "Binance Coin", "supports_technical_analysis": True},
            {"symbol": "SOL", "name": "Solana", "supports_technical_analysis": True},
            {"symbol": "MATIC", "name": "Polygon", "supports_technical_analysis": True},
        ]
        
        return SupportedSymbolsResponse(
            success=True,
            symbols=symbols
        )
    except Exception as e:
        logger.error(f"获取支持币种失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/technical-analysis", response_model=TechnicalAnalysisResponse)
async def analyze_technical_indicators(request: TechnicalAnalysisRequest):
    """技术分析API"""
    try:
        # 设置历史数据管理器
        technical_analyzer.historical_data_manager = historical_data_manager
        
        # 执行技术分析
        result = await technical_analyzer.analyze(
            symbol=request.symbol,
            indicators=request.indicators,
            timeframe=request.timeframe,
            period=request.period
        )
        
        # 构建响应
        indicators_dict = {}
        
        if result.rsi is not None:
            indicators_dict['rsi'] = result.rsi
        
        if result.macd is not None:
            indicators_dict['macd'] = result.macd
        
        if result.bollinger_bands is not None:
            indicators_dict['bollinger_bands'] = result.bollinger_bands
        
        if result.sma_20 is not None:
            indicators_dict['sma_20'] = result.sma_20
        
        if result.sma_50 is not None:
            indicators_dict['sma_50'] = result.sma_50
        
        if result.ema_12 is not None:
            indicators_dict['ema_12'] = result.ema_12
        
        if result.ema_26 is not None:
            indicators_dict['ema_26'] = result.ema_26
        
        if result.stochastic is not None:
            indicators_dict['stochastic'] = result.stochastic
        
        if result.williams_r is not None:
            indicators_dict['williams_r'] = result.williams_r
        
        if result.cci is not None:
            indicators_dict['cci'] = result.cci
        
        if result.momentum is not None:
            indicators_dict['momentum'] = result.momentum
        
        return TechnicalAnalysisResponse(
            success=True,
            symbol=result.symbol,
            timeframe=result.timeframe,
            timestamp=result.timestamp.isoformat(),
            data_points_used=result.data_points_used,
            calculation_time_ms=result.calculation_time_ms or 0,
            indicators=indicators_dict,
            signals=result.get_signals()
        )
        
    except Exception as e:
        logger.error(f"技术分析失败: {e}")
        return TechnicalAnalysisResponse(
            success=False,
            symbol=request.symbol,
            timeframe=request.timeframe,
            timestamp=datetime.now().isoformat(),
            data_points_used=0,
            calculation_time_ms=0,
            indicators={},
            signals={},
            error=str(e)
        )

@app.get("/api/v1/historical-data", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str = Query(..., description="币种代码"),
    timeframe: str = Query("1h", description="时间框架"),
    period: str = Query("30d", description="历史数据周期")
):
    """获取历史数据API"""
    try:
        data = await historical_data_manager.get_data(
            symbol=symbol,
            interval=timeframe,
            period=period
        )
        
        return HistoricalDataResponse(
            success=True,
            symbol=symbol,
            timeframe=timeframe,
            data_count=len(data),
            data=data
        )
        
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        return HistoricalDataResponse(
            success=False,
            symbol=symbol,
            timeframe=timeframe,
            data_count=0,
            data=[],
            error=str(e)
        )

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0"
    }

# 启动函数
def create_app():
    """创建应用实例"""
    return app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )