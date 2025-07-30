#!/usr/bin/env python3
"""
最简单的 AutoGen 测试
用于快速验证 API 兼容性
"""

import os
from dotenv import load_dotenv
from rich.console import Console

# 加载环境变量
load_dotenv()

console = Console()

def test_minimal_autogen():
    """测试最基础的AutoGen功能"""
    
    console.print("[blue]🧪 开始最简单的 AutoGen 测试[/blue]")
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("❌ [red]未找到 OPENAI_API_KEY，请检查 .env 文件[/red]")
        console.print("💡 [yellow]运行 python check_env.py 检查配置[/yellow]")
        return False
    
    console.print("✅ [green]API 密钥已设置[/green]")
    
    try:
        # 导入AutoGen
        import autogen
        from autogen import AssistantAgent, UserProxyAgent
        console.print("✅ [green]AutoGen 导入成功[/green]")
        
        # 创建最简单的配置
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",  # 使用便宜的模型进行测试
                    "api_key": api_key,
                }
            ],
            "timeout": 60,
            "temperature": 0,
        }
        
        # 创建最简单的Agent
        assistant = AssistantAgent(
            name="SimpleAssistant",
            system_message="你是一个简单的助手。请用一句话回复。",
            llm_config=llm_config,
        )
        
        user_proxy = UserProxyAgent(
            name="SimpleUser",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
        
        console.print("✅ [green]Agents 创建成功[/green]")
        
        # 进行最简单的对话测试
        console.print("🔄 [blue]测试简单对话...[/blue]")
        
        result = user_proxy.initiate_chat(
            assistant,
            message="请说'测试成功'"
        )
        
        console.print("✅ [green]对话测试完成[/green]")
        console.print(f"📊 [dim]结果类型: {type(result)}[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]测试失败: {e}[/red]")
        
        # 提供详细的错误信息
        import traceback
        console.print(f"[dim]详细错误:[/dim]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        return False

def main():
    """主函数"""
    
    console.print("""
[bold blue]🚀 AutoGen 最简测试工具[/bold blue]

这个工具用于验证基础的 AutoGen 功能：
• 检查 API 密钥配置
• 测试 Agent 创建
• 验证简单对话

如果这个测试通过，说明基础环境配置正确。
如果失败，请先解决基础问题再运行完整 Demo。
""")
    
    success = test_minimal_autogen()
    
    if success:
        console.print("""
[bold green]🎉 测试通过！[/bold green]

✅ 基础 AutoGen 功能正常
✅ API 配置正确
✅ 可以继续运行完整演示

[cyan]下一步：[/cyan]
python demo.py run-demo "分析电动汽车市场"
""")
    else:
        console.print("""
[bold red]❌ 测试失败[/bold red]

请检查以下问题：
1. .env 文件是否存在且配置正确
2. OpenAI API 密钥是否有效
3. 网络连接是否正常
4. AutoGen 库是否正确安装

[cyan]故障排除：[/cyan]
1. 检查配置：python check_env.py
2. 重新安装：pip install -r requirements.txt
3. 检查 API 配额和余额
""")

if __name__ == "__main__":
    main() 