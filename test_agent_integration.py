#!/usr/bin/env python3
"""
Agent集成测试脚本
测试各种集成方式是否正常工作
"""

import json
import time
import requests
import subprocess
import sys
from typing import Dict, Any

class AgentIntegrationTester:
    def __init__(self):
        self.api_base_url = "http://localhost:5000"
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_api_server(self) -> bool:
        """测试API服务器是否运行"""
        try:
            response = requests.get(f"{self.api_base_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("API服务器连接", True, "Flask服务正常运行")
                return True
            else:
                self.log_test("API服务器连接", False, f"HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_test("API服务器连接", False, "无法连接到API服务器，请先运行 python app.py")
            return False
        except Exception as e:
            self.log_test("API服务器连接", False, str(e))
            return False
    
    def test_crypto_agent(self) -> bool:
        """测试基础Agent功能"""
        try:
            from crypto_agent import crypto_agent
            
            # 测试价格查询
            result = crypto_agent.process_query("BTC价格")
            if "BTC" in result and ("$" in result or "价格" in result):
                self.log_test("基础Agent查询", True, "BTC价格查询成功")
                success = True
            else:
                self.log_test("基础Agent查询", False, "查询结果格式异常")
                success = False
            
            # 测试市场概览
            overview = crypto_agent.get_market_overview()
            if "BTC" in overview and "ETH" in overview:
                self.log_test("市场概览功能", True, "市场概览获取成功")
            else:
                self.log_test("市场概览功能", False, "市场概览格式异常")
                success = False
            
            return success
            
        except ImportError as e:
            self.log_test("基础Agent查询", False, f"导入错误: {e}")
            return False
        except Exception as e:
            self.log_test("基础Agent查询", False, str(e))
            return False
    
    def test_api_endpoints(self) -> bool:
        """测试API端点"""
        try:
            # 测试单个查询
            response = requests.get(f"{self.api_base_url}/api/crypto/BTC", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "symbol" in data and "price" in data:
                    self.log_test("API端点查询", True, "BTC API查询成功")
                    success = True
                else:
                    self.log_test("API端点查询", False, "API响应格式异常")
                    success = False
            else:
                self.log_test("API端点查询", False, f"HTTP {response.status_code}")
                success = False
            
            return success
            
        except Exception as e:
            self.log_test("API端点查询", False, str(e))
            return False
    
    def test_mcp_server(self) -> bool:
        """测试MCP服务器"""
        try:
            # 检查MCP服务器文件是否存在
            import os
            if not os.path.exists("crypto_mcp_server.py"):
                self.log_test("MCP服务器文件", False, "crypto_mcp_server.py 不存在")
                return False
            
            # 测试配置生成
            result = subprocess.run([
                sys.executable, "crypto_mcp_server.py", "config"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_test("MCP配置生成", True, "MCP配置文件生成成功")
                
                # 检查配置文件是否创建
                if os.path.exists("mcp_config.json"):
                    with open("mcp_config.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    if "mcpServers" in config and "crypto-price-checker" in config["mcpServers"]:
                        self.log_test("MCP配置验证", True, "配置文件格式正确")
                        return True
                    else:
                        self.log_test("MCP配置验证", False, "配置文件格式错误")
                        return False
                else:
                    self.log_test("MCP配置验证", False, "配置文件未创建")
                    return False
            else:
                self.log_test("MCP配置生成", False, result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_test("MCP服务器测试", False, "测试超时")
            return False
        except Exception as e:
            self.log_test("MCP服务器测试", False, str(e))
            return False
    
    def test_integrations(self) -> bool:
        """测试集成功能"""
        try:
            from agent_integrations import CryptoAgentPlugin, handle_openai_function_call
            
            # 测试自定义插件
            plugin = CryptoAgentPlugin()
            capabilities = plugin.get_capabilities()
            
            if len(capabilities) >= 3:
                self.log_test("自定义插件", True, f"插件支持 {len(capabilities)} 个功能")
                
                # 测试插件执行
                result = plugin.execute("query_price", symbol="BTC")
                if "BTC" in result:
                    self.log_test("插件执行测试", True, "插件功能执行成功")
                    success = True
                else:
                    self.log_test("插件执行测试", False, "插件执行结果异常")
                    success = False
            else:
                self.log_test("自定义插件", False, "插件功能数量不足")
                success = False
            
            # 测试OpenAI Function Calling
            function_call = {
                "arguments": json.dumps({"symbol": "ETH", "query_type": "price"})
            }
            result = handle_openai_function_call(function_call)
            if "ETH" in result:
                self.log_test("OpenAI Function Calling", True, "函数调用测试成功")
            else:
                self.log_test("OpenAI Function Calling", False, "函数调用结果异常")
                success = False
            
            return success
            
        except ImportError as e:
            self.log_test("集成功能测试", False, f"导入错误: {e}")
            return False
        except Exception as e:
            self.log_test("集成功能测试", False, str(e))
            return False
    
    def test_natural_language(self) -> bool:
        """测试自然语言处理"""
        try:
            from crypto_agent import crypto_agent
            
            test_queries = [
                "BTC价格",
                "比特币多少钱",
                "查询以太坊",
                "告诉我SOL的价格",
                "bitcoin price"
            ]
            
            success_count = 0
            for query in test_queries:
                result = crypto_agent.process_query(query)
                if not result.startswith("❓"):  # 不是"未识别"错误
                    success_count += 1
            
            if success_count >= len(test_queries) * 0.8:  # 80%成功率
                self.log_test("自然语言处理", True, f"{success_count}/{len(test_queries)} 查询成功")
                return True
            else:
                self.log_test("自然语言处理", False, f"仅 {success_count}/{len(test_queries)} 查询成功")
                return False
                
        except Exception as e:
            self.log_test("自然语言处理", False, str(e))
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始Agent集成测试")
        print("=" * 50)
        
        # 测试顺序很重要
        tests = [
            ("API服务器", self.test_api_server),
            ("基础Agent功能", self.test_crypto_agent),
            ("API端点", self.test_api_endpoints),
            ("自然语言处理", self.test_natural_language),
            ("MCP服务器", self.test_mcp_server),
            ("集成功能", self.test_integrations),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 测试: {test_name}")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"测试异常: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！Agent集成准备就绪。")
            return True
        else:
            print("⚠️  部分测试失败，请检查相关配置。")
            return False
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": len(self.test_results),
            "passed": sum(1 for r in self.test_results if r["success"]),
            "failed": sum(1 for r in self.test_results if not r["success"]),
            "results": self.test_results
        }
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 测试报告已保存到: test_report.json")

def main():
    """主函数"""
    tester = AgentIntegrationTester()
    
    try:
        success = tester.run_all_tests()
        tester.generate_test_report()
        
        if success:
            print("\n🚀 快速开始:")
            print("1. 启动API服务: python app.py")
            print("2. 测试Agent: python crypto_agent.py")
            print("3. 配置MCP: python crypto_mcp_server.py config")
            print("4. 查看集成指南: AGENT_INTEGRATION_GUIDE.md")
        else:
            print("\n🔧 故障排除:")
            print("1. 确保API服务正在运行")
            print("2. 检查网络连接")
            print("3. 验证Python依赖")
            print("4. 查看测试报告: test_report.json")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())