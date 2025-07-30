"""
简化测试Demo - 用于调试AutoGen API兼容性
"""

import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

console = Console()

def test_basic_autogen():
    """测试基础的AutoGen功能"""
    try:
        import autogen
        from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
        
        console.print("✅ AutoGen导入成功", style="green")
        
        # 检查API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("❌ 未设置OPENAI_API_KEY", style="red")
            return False
        
        console.print("✅ API密钥已设置", style="green")
        
        # 创建基础配置
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": api_key,
                }
            ],
            "timeout": 120,
            "temperature": 0.1,
        }
        
        # 创建简单的Agent
        assistant = AssistantAgent(
            name="TestAssistant",
            system_message="你是一个测试助手。请简短回复。",
            llm_config=llm_config,
        )
        
        user_proxy = UserProxyAgent(
            name="TestUser",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
        
        console.print("✅ Agent创建成功", style="green")
        
        # 测试简单对话
        console.print("🔄 测试简单对话...", style="blue")
        
        result = user_proxy.initiate_chat(
            assistant,
            message="请说'你好，这是一个测试'"
        )
        
        console.print("✅ 简单对话测试成功", style="green")
        console.print(f"结果类型: {type(result)}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ 测试失败: {e}", style="red")
        import traceback
        console.print(f"详细错误: {traceback.format_exc()}", style="red")
        return False

def test_group_chat():
    """测试群聊功能"""
    try:
        import autogen
        from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print("❌ 未设置OPENAI_API_KEY", style="red")
            return False
        
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-3.5-turbo",
                    "api_key": api_key,
                }
            ],
            "timeout": 120,
            "temperature": 0.1,
        }
        
        # 创建多个Agent
        assistant1 = AssistantAgent(
            name="Assistant1",
            system_message="你是助手1，请简短回复。",
            llm_config=llm_config,
        )
        
        assistant2 = AssistantAgent(
            name="Assistant2", 
            system_message="你是助手2，请简短回复。",
            llm_config=llm_config,
        )
        
        user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
        
        # 创建群聊
        group_chat = GroupChat(
            agents=[assistant1, assistant2, user_proxy],
            messages=[],
            max_round=3,
        )
        
        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config=llm_config,
        )
        
        console.print("✅ 群聊创建成功", style="green")
        
        # 测试群聊
        console.print("🔄 测试群聊对话...", style="blue")
        
        result = user_proxy.initiate_chat(
            manager,
            message="请大家依次说'你好'",
            max_turns=3
        )
        
        console.print("✅ 群聊测试成功", style="green")
        console.print(f"结果类型: {type(result)}")
        
        # 打印群聊消息
        console.print("\n📋 群聊消息:")
        for i, msg in enumerate(group_chat.messages):
            console.print(f"  {i+1}. {msg}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ 群聊测试失败: {e}", style="red")
        import traceback
        console.print(f"详细错误: {traceback.format_exc()}", style="red")
        return False

async def test_simplified_workflow():
    """测试简化的工作流"""
    try:
        from src.agents import create_market_analysis_team
        
        console.print("🔄 创建市场分析团队...", style="blue")
        team = create_market_analysis_team()
        console.print("✅ 团队创建成功", style="green")
        
        console.print("🔄 执行简单分析...", style="blue")
        
        # 使用非常简单的查询
        simple_query = "简单说明电动汽车的优势"
        
        result = await team.analyze_market(simple_query)
        
        if result:
            console.print("✅ 分析成功", style="green")
            console.print(f"结果长度: {len(result.content)}")
            console.print(f"可信度: {result.confidence}")
        else:
            console.print("❌ 分析失败", style="red")
            
        return result is not None
        
    except Exception as e:
        console.print(f"❌ 工作流测试失败: {e}", style="red")
        import traceback
        console.print(f"详细错误: {traceback.format_exc()}", style="red")
        return False

def main():
    """主测试函数"""
    console.print(
        Panel(
            "[bold blue]AutoGen API 兼容性测试[/bold blue]\n\n"
            "[white]测试项目:[/white]\n"
            "• 基础 AutoGen 功能\n"
            "• 群聊功能\n"
            "• 简化工作流\n",
            title="🧪 测试开始",
            border_style="blue"
        )
    )
    
    # 测试1: 基础功能
    console.print("\n[bold]测试1: 基础AutoGen功能[/bold]")
    basic_ok = test_basic_autogen()
    
    if not basic_ok:
        console.print("❌ 基础测试失败，跳过后续测试", style="red")
        return
    
    # 测试2: 群聊功能
    console.print("\n[bold]测试2: 群聊功能[/bold]")
    group_ok = test_group_chat()
    
    if not group_ok:
        console.print("❌ 群聊测试失败，跳过工作流测试", style="red")
        return
    
    # 测试3: 简化工作流
    console.print("\n[bold]测试3: 简化工作流[/bold]")
    
    async def run_workflow_test():
        return await test_simplified_workflow()
    
    workflow_ok = asyncio.run(run_workflow_test())
    
    # 总结
    console.print(
        Panel(
            f"[bold]测试结果总结[/bold]\n\n"
            f"• 基础功能: {'✅ 通过' if basic_ok else '❌ 失败'}\n"
            f"• 群聊功能: {'✅ 通过' if group_ok else '❌ 失败'}\n"
            f"• 简化工作流: {'✅ 通过' if workflow_ok else '❌ 失败'}\n",
            title="🎯 测试总结",
            border_style="green" if all([basic_ok, group_ok, workflow_ok]) else "red"
        )
    )

if __name__ == "__main__":
    main() 