#!/usr/bin/env python3
"""
测试 OpenTelemetry Instrumentation 
验证是否能正确捕获 LLM 调用的输入输出内容
"""

import os
import asyncio
import openai
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.observability import ObservabilityManager
from src.config import config

console = Console()

async def test_openai_instrumentation():
    """测试 OpenAI instrumentation 是否捕获内容"""
    console.print(Panel("🧪 测试 OpenAI Instrumentation", style="blue"))
    
    # 初始化可观测性
    obs_manager = ObservabilityManager()
    obs_manager.initialize()
    
    # 检查API密钥
    if not config.llm.openai_api_key:
        console.print("❌ [red]未设置 OPENAI_API_KEY[/red]")
        return
    
    # 创建 OpenAI 客户端
    client = openai.OpenAI(api_key=config.llm.openai_api_key)
    
    console.print("📡 [blue]发送测试请求到 OpenAI...[/blue]")
    
    try:
        # 发送简单的测试请求
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用较便宜的模型进行测试
            messages=[
                {"role": "system", "content": "你是一个测试助手，请简洁回答。"},
                {"role": "user", "content": "请说'测试成功'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        console.print(f"✅ [green]OpenAI 响应: {result}[/green]")
        
        # 显示token使用情况
        if response.usage:
            table = Table(title="Token 使用情况")
            table.add_column("类型", style="cyan")
            table.add_column("数量", style="yellow")
            
            table.add_row("输入Token", str(response.usage.prompt_tokens))
            table.add_row("输出Token", str(response.usage.completion_tokens))
            table.add_row("总计Token", str(response.usage.total_tokens))
            
            console.print(table)
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]OpenAI 调用失败: {e}[/red]")
        return False

def test_agent_tracing():
    """测试 Agent 追踪功能"""
    console.print(Panel("🤖 测试 Agent 追踪", style="green"))
    
    # 初始化可观测性
    obs_manager = ObservabilityManager()
    obs_manager.initialize()
    
    # 使用追踪装饰器测试
    @obs_manager.trace_agent_operation("test_agent_operation")
    def test_agent_function(input_message: str) -> str:
        """测试用的agent函数"""
        console.print(f"🔄 [yellow]处理消息: {input_message}[/yellow]")
        return f"已处理: {input_message}"
    
    # 执行测试
    test_messages = [
        "测试消息1：分析市场趋势",
        "测试消息2：生成投资建议", 
        "测试消息3：风险评估报告"
    ]
    
    for msg in test_messages:
        result = test_agent_function(msg)
        console.print(f"📤 [green]输出: {result}[/green]")
    
    return True

async def run_complete_test():
    """运行完整的测试流程"""
    console.print("🚀 [bold blue]OpenTelemetry Instrumentation 测试[/bold blue]\n")
    
    # 测试1：Agent追踪
    agent_test_result = test_agent_tracing()
    console.print()
    
    # 测试2：OpenAI instrumentation
    openai_test_result = await test_openai_instrumentation()
    console.print()
    
    # 显示结果总结
    results_table = Table(title="测试结果总结")
    results_table.add_column("测试项目", style="cyan")
    results_table.add_column("状态", style="green")
    results_table.add_column("说明", style="yellow")
    
    results_table.add_row(
        "Agent 追踪", 
        "✅ 通过" if agent_test_result else "❌ 失败",
        "自定义追踪功能"
    )
    
    results_table.add_row(
        "OpenAI Instrumentation",
        "✅ 通过" if openai_test_result else "❌ 失败", 
        "LLM调用自动追踪"
    )
    
    console.print(results_table)
    
    # 提示用户查看Phoenix UI
    phoenix_port = config.observability.phoenix_port
    console.print(f"\n🌐 [bold green]查看追踪数据: http://localhost:{phoenix_port}[/bold green]")
    console.print("💡 [blue]在Phoenix UI中应该能看到包含input/output的trace数据[/blue]")
    
    # 提供具体的检查步骤
    console.print(Panel(
        "🔍 Phoenix UI 检查步骤:\n\n"
        "1. 打开 http://localhost:6006\n"
        "2. 点击 'Traces' 标签\n"
        "3. 查看最新的 trace 记录\n"
        "4. 展开 span 查看 input/output 字段\n"
        "5. 确认不再显示 '--'",
        title="检查指南",
        style="cyan"
    ))

if __name__ == "__main__":
    asyncio.run(run_complete_test()) 