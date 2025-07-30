#!/usr/bin/env python3
"""
专门用于调试 Agent 问题的测试脚本
快速定位 generate_reply 相关问题
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console

# 加载环境变量
load_dotenv()

console = Console()

def test_tracked_agent():
    """测试TrackedAssistantAgent的基本功能"""
    
    console.print("[blue]🔍 测试 TrackedAssistantAgent[/blue]")
    
    try:
        # 导入我们的模块
        from src.agents import TrackedAssistantAgent
        from src.config import config
        
        console.print("✅ [green]模块导入成功[/green]")
        
        # 创建配置
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": config.llm.openai_api_key,
                }
            ],
            "timeout": 60,
            "temperature": 0,
        }
        
        # 创建TrackedAssistantAgent
        agent = TrackedAssistantAgent(
            name="TestAgent",
            system_message="你是一个测试助手，请简短回复。",
            llm_config=llm_config,
        )
        
        console.print("✅ [green]TrackedAssistantAgent 创建成功[/green]")
        
        # 测试1: 直接调用generate_reply
        console.print("🧪 [blue]测试1: 直接调用 generate_reply[/blue]")
        
        messages = [{"role": "user", "content": "请说'测试1成功'"}]
        
        try:
            reply1 = agent.generate_reply(messages)
            console.print(f"✅ [green]测试1成功: {reply1}[/green]")
        except Exception as e:
            console.print(f"❌ [red]测试1失败: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        # 测试2: 使用不同的参数格式
        console.print("🧪 [blue]测试2: 不同参数格式[/blue]")
        
        try:
            reply2 = agent.generate_reply(messages=messages, sender=None)
            console.print(f"✅ [green]测试2成功: {reply2}[/green]")
        except Exception as e:
            console.print(f"❌ [red]测试2失败: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        # 测试3: 模拟AutoGen内部调用方式
        console.print("🧪 [blue]测试3: 模拟AutoGen内部调用[/blue]")
        
        try:
            # 尝试不同的调用方式
            reply3 = agent.generate_reply(messages, None)
            console.print(f"✅ [green]测试3成功: {reply3}[/green]")
        except Exception as e:
            console.print(f"❌ [red]测试3失败: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]整体测试失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

def test_simple_workflow():
    """测试最简单的工作流"""
    
    console.print("[blue]🔧 测试简单工作流[/blue]")
    
    try:
        from src.agents import MarketAnalysisTeam
        
        # 创建团队
        team = MarketAnalysisTeam()
        console.print("✅ [green]团队创建成功[/green]")
        
        # 测试单个Agent的generate_reply
        console.print("🧪 [blue]测试单个Agent[/blue]")
        
        writer = team.agents["writer"]
        messages = [{"role": "user", "content": "请说'工作流测试成功'"}]
        
        try:
            reply = writer.generate_reply(messages)
            console.print(f"✅ [green]单Agent测试成功: {reply}[/green]")
        except Exception as e:
            console.print(f"❌ [red]单Agent测试失败: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]工作流测试失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

def main():
    """主函数"""
    
    console.print("""
[bold blue]🔍 Agent 调试工具[/bold blue]

专门用于诊断 generate_reply 相关问题：
• 测试 TrackedAssistantAgent 基本功能
• 验证不同的参数调用方式  
• 模拟 AutoGen 内部调用模式
""")
    
    # 检查基础配置
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("❌ [red]未找到 OPENAI_API_KEY[/red]")
        console.print("💡 [yellow]请运行: python check_env.py[/yellow]")
        return
    
    console.print("✅ [green]API 密钥配置正确[/green]")
    
    # 运行测试
    console.print("\n" + "="*50)
    test1_ok = test_tracked_agent()
    
    console.print("\n" + "="*50)
    test2_ok = test_simple_workflow()
    
    # 总结
    console.print("\n" + "="*50)
    console.print(f"[bold]测试结果:[/bold]")
    console.print(f"• TrackedAgent 测试: {'✅ 通过' if test1_ok else '❌ 失败'}")
    console.print(f"• 简单工作流测试: {'✅ 通过' if test2_ok else '❌ 失败'}")
    
    if test1_ok and test2_ok:
        console.print("\n🎉 [bold green]所有测试通过！可以运行完整演示。[/bold green]")
    else:
        console.print("\n⚠️ [bold yellow]存在问题，请检查错误信息。[/bold yellow]")

if __name__ == "__main__":
    main() 