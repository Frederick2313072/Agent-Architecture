#!/usr/bin/env python3
"""
测试 OpenInference Instrumentation
验证是否能正确捕获 LLM 调用的输入输出内容
"""

import os
import sys
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_dependencies():
    """检查新的依赖是否可用"""
    console.print(Panel("🔍 检查 OpenInference 依赖", style="blue"))
    
    missing_deps = []
    
    try:
        import openinference.instrumentation.openai
        console.print("✅ [green]openinference-instrumentation-openai 可用[/green]")
    except ImportError as e:
        console.print(f"❌ [red]openinference-instrumentation-openai 缺失: {e}[/red]")
        missing_deps.append("openinference-instrumentation-openai")
    
    try:
        import openinference.instrumentation.anthropic
        console.print("✅ [green]openinference-instrumentation-anthropic 可用[/green]")
    except ImportError as e:
        console.print(f"❌ [red]openinference-instrumentation-anthropic 缺失: {e}[/red]")
        missing_deps.append("openinference-instrumentation-anthropic")
    
    try:
        import phoenix as px
        console.print("✅ [green]arize-phoenix 可用[/green]")
    except ImportError as e:
        console.print(f"❌ [red]arize-phoenix 缺失: {e}[/red]")
        missing_deps.append("arize-phoenix")
    
    if missing_deps:
        console.print(f"\n📦 [yellow]需要安装缺失的依赖:[/yellow]")
        console.print("运行以下命令:")
        console.print(f"[cyan]pip install {' '.join(missing_deps)}[/cyan]")
        return False
    
    return True

def test_instrumentation_import():
    """测试新的instrumentation导入"""
    console.print(Panel("🧪 测试 Instrumentation 导入", style="green"))
    
    try:
        from src.observability import ObservabilityManager
        console.print("✅ [green]ObservabilityManager 导入成功[/green]")
        
        # 尝试初始化
        obs_manager = ObservabilityManager()
        console.print("✅ [green]ObservabilityManager 创建成功[/green]")
        
        # 尝试初始化（这会测试新的instrumentation）
        obs_manager.initialize()
        console.print("✅ [green]ObservabilityManager 初始化成功[/green]")
        
        return True
        
    except ImportError as e:
        console.print(f"❌ [red]导入失败: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"⚠️ [yellow]初始化过程中出现问题: {e}[/yellow]")
        return False

async def test_openai_call():
    """测试OpenAI调用是否被正确追踪"""
    console.print(Panel("📡 测试 OpenAI 调用追踪", style="cyan"))
    
    try:
        # 检查API密钥
        from src.config import config
        if not config.llm.openai_api_key:
            console.print("⚠️ [yellow]未设置 OPENAI_API_KEY，跳过实际调用测试[/yellow]")
            return True
        
        import openai
        from src.observability import ObservabilityManager
        
        # 初始化观测系统
        obs_manager = ObservabilityManager()
        obs_manager.initialize()
        
        # 创建OpenAI客户端
        client = openai.OpenAI(api_key=config.llm.openai_api_key)
        
        # 发送测试请求
        console.print("🚀 [blue]发送测试请求...[/blue]")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请简单说'Hello Phoenix!'"}
            ],
            max_tokens=20,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        console.print(f"✅ [green]OpenAI 响应: {result}[/green]")
        
        # 显示使用信息
        if response.usage:
            table = Table(title="调用信息")
            table.add_column("指标", style="cyan")
            table.add_column("值", style="yellow")
            
            table.add_row("输入Token", str(response.usage.prompt_tokens))
            table.add_row("输出Token", str(response.usage.completion_tokens))
            table.add_row("总Token", str(response.usage.total_tokens))
            
            console.print(table)
        
        return True
        
    except Exception as e:
        console.print(f"❌ [red]OpenAI 调用测试失败: {e}[/red]")
        return False

async def main():
    """主测试函数"""
    console.print("🚀 [bold blue]OpenInference Instrumentation 测试[/bold blue]\n")
    
    # 步骤1：检查依赖
    deps_ok = check_dependencies()
    if not deps_ok:
        console.print("\n❌ [red]请先安装缺失的依赖，然后重新运行测试[/red]")
        sys.exit(1)
    
    console.print()
    
    # 步骤2：测试导入
    import_ok = test_instrumentation_import()
    console.print()
    
    # 步骤3：测试实际调用（如果前面成功）
    if import_ok:
        call_ok = await test_openai_call()
        console.print()
    else:
        call_ok = False
    
    # 结果总结
    results_table = Table(title="测试结果")
    results_table.add_column("测试项", style="cyan")
    results_table.add_column("状态", style="green")
    
    results_table.add_row("依赖检查", "✅ 通过" if deps_ok else "❌ 失败")
    results_table.add_row("导入测试", "✅ 通过" if import_ok else "❌ 失败")
    results_table.add_row("调用测试", "✅ 通过" if call_ok else "❌ 失败")
    
    console.print(results_table)
    
    if deps_ok and import_ok and call_ok:
        console.print(f"\n🎉 [bold green]所有测试通过！现在访问 Phoenix UI 查看追踪数据:[/bold green]")
        console.print(f"🌐 [cyan]http://localhost:6006[/cyan]")
        console.print("\n💡 [blue]在新的 OpenInference instrumentation 下，input 和 output 字段应该显示实际内容而不是 '--'[/blue]")
    else:
        console.print(f"\n❌ [red]测试未完全通过，请检查上述错误信息[/red]")

if __name__ == "__main__":
    asyncio.run(main()) 