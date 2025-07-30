"""
AutoGen Agent Workflow 完整演示
展示对话驱动的多Agent协作、可观测性和安全机制
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.json import JSON
import typer

from .config import config, validate_config
from .observability import observability
from .agents import create_market_analysis_team
from .safety import AgentOutput

# 初始化富文本控制台
console = Console()
app = typer.Typer(rich_markup_mode="rich")

class DemoOrchestrator:
    """演示编排器"""
    
    def __init__(self):
        self.team = None
        self.results = {}
    
    async def initialize_system(self):
        """初始化整个系统"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # 1. 验证配置
            task1 = progress.add_task("🔧 验证配置...", total=None)
            try:
                validate_config()
                progress.update(task1, description="✅ 配置验证完成")
            except Exception as e:
                console.print(f"❌ 配置验证失败: {e}", style="red")
                sys.exit(1)
            
            # 2. 初始化可观测性系统
            task2 = progress.add_task("📊 启动可观测性系统...", total=None)
            try:
                observability.initialize()
                progress.update(task2, description="✅ 可观测性系统就绪")
            except Exception as e:
                console.print(f"⚠️ 可观测性系统启动失败: {e}", style="yellow")
            
            # 3. 创建Agent团队
            task3 = progress.add_task("🤖 创建Agent团队...", total=None)
            try:
                self.team = create_market_analysis_team()
                progress.update(task3, description="✅ Agent团队创建完成")
            except Exception as e:
                console.print(f"❌ Agent团队创建失败: {e}", style="red")
                sys.exit(1)
    
    async def run_market_analysis_demo(self, query: str):
        """运行市场分析演示"""
        
        # 显示任务开始面板
        console.print(
            Panel(
                f"[bold blue]🎯 市场分析任务[/bold blue]\n\n"
                f"[white]查询:[/white] [italic]{query}[/italic]\n\n"
                f"[dim]系统将启动多Agent协作流程...[/dim]",
                title="AutoGen Agent Workflow",
                border_style="blue"
            )
        )
        
        # 执行分析
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("🤖 Agent团队协作中...", total=None)
            
            try:
                result = await self.team.analyze_market(query)
                progress.update(task, description="✅ 分析完成")
                
                if result:
                    await self._display_results(result)
                    await self._display_conversation_summary()
                else:
                    console.print("❌ 分析失败，未能生成有效结果", style="red")
                    
            except Exception as e:
                progress.update(task, description="❌ 分析失败")
                console.print(f"执行过程中出现错误: {e}", style="red")
    
    async def _display_results(self, result: AgentOutput):
        """展示分析结果"""
        
        # 主要结果面板
        console.print(
            Panel(
                result.content,
                title=f"📊 [bold green]{result.agent_name} 分析结果[/bold green]",
                border_style="green"
            )
        )
        
        # 元数据表格
        metadata_table = Table(title="🔍 结果元数据")
        metadata_table.add_column("属性", style="cyan")
        metadata_table.add_column("值", style="white")
        
        metadata_table.add_row("可信度评分", f"{result.confidence:.2f}")
        metadata_table.add_row("生成Agent", result.agent_name)
        metadata_table.add_row("信息来源数", str(len(result.sources)))
        
        for key, value in result.metadata.items():
            metadata_table.add_row(key, str(value))
        
        console.print(metadata_table)
        
        # 如果有来源信息，显示来源
        if result.sources:
            sources_panel = Panel(
                "\n".join(f"• {source}" for source in result.sources),
                title="📚 信息来源",
                border_style="yellow"
            )
            console.print(sources_panel)
    
    async def _display_conversation_summary(self):
        """显示对话摘要"""
        summary = self.team.get_conversation_summary()
        
        summary_table = Table(title="💬 对话协作摘要")
        summary_table.add_column("指标", style="cyan")
        summary_table.add_column("值", style="white")
        
        summary_table.add_row("总轮次", str(summary["total_rounds"]))
        summary_table.add_row("参与Agent数", str(len(summary["participants"])))
        summary_table.add_row("消息总数", str(summary["message_count"]))
        
        console.print(summary_table)
        
        # Agent贡献分布
        if summary["agent_contributions"]:
            contrib_table = Table(title="🤝 Agent贡献分布")
            contrib_table.add_column("Agent", style="cyan")
            contrib_table.add_column("消息数", style="white")
            
            for agent_name, count in summary["agent_contributions"].items():
                contrib_table.add_row(agent_name, str(count))
            
            console.print(contrib_table)

@app.command()
def run_demo(
    query: str = typer.Argument(..., help="市场分析查询"),
    config_check: bool = typer.Option(False, "--check-config", help="仅检查配置")
):
    """
    运行 AutoGen Agent Workflow 演示
    
    展示对话驱动的多Agent协作、全方位可观测性和安全验证机制。
    """
    
    if config_check:
        console.print("🔧 检查系统配置...")
        try:
            validate_config()
            console.print("✅ 配置验证通过", style="green")
            
            # 检查.env文件是否存在
            env_exists = os.path.exists(".env")
            
            # 显示配置摘要
            config_table = Table(title="配置摘要")
            config_table.add_column("类别", style="cyan")
            config_table.add_column("状态", style="white")
            
            config_table.add_row(".env文件", "✅ 存在" if env_exists else "❌ 不存在（建议创建）")
            config_table.add_row("OpenAI API", "✅ 已配置" if config.llm.openai_api_key else "❌ 未配置")
            config_table.add_row("默认模型", config.llm.default_model)
            config_table.add_row("内容审核", "✅ 启用" if config.security.enable_content_moderation else "❌ 禁用")
            config_table.add_row("追踪系统", "✅ 启用" if config.observability.enable_tracing else "❌ 禁用")
            
            if not env_exists:
                console.print(
                    Panel(
                        "[yellow]💡 建议创建 .env 文件[/yellow]\n\n"
                        "[white]步骤:[/white]\n"
                        "1. 复制模板：[cyan]cp env_template.txt .env[/cyan]\n"
                        "2. 编辑文件：[cyan]nano .env[/cyan]\n"
                        "3. 填入您的 OpenAI API 密钥",
                        title="配置建议",
                        border_style="yellow"
                    )
                )
            
            console.print(config_table)
            
        except Exception as e:
            console.print(f"❌ 配置检查失败: {e}", style="red")
            sys.exit(1)
        return
    
    # 运行完整演示
    async def main():
        demo = DemoOrchestrator()
        
        # 显示欢迎信息
        console.print(
            Panel(
                "[bold blue]AutoGen Agent Workflow 演示[/bold blue]\n\n"
                "[white]特性展示:[/white]\n"
                "• 🤖 对话驱动的多Agent协作\n"
                "• 📊 OpenTelemetry + Phoenix 可观测性\n"
                "• 🛡️ 内容安全与输出验证\n"
                "• 🔄 自修复与容错机制\n\n"
                f"[dim]查询: {query}[/dim]",
                title="🚀 系统启动",
                border_style="blue"
            )
        )
        
        # 初始化系统
        await demo.initialize_system()
        
        # 运行演示
        await demo.run_market_analysis_demo(query)
        
        # 显示追踪信息
        if config.observability.enable_tracing:
            console.print(
                Panel(
                    f"🔍 追踪数据已记录到 Phoenix UI\n"
                    f"🌐 访问: http://localhost:{config.observability.phoenix_port}",
                    title="可观测性",
                    border_style="yellow"
                )
            )
    
    # 运行异步主函数
    asyncio.run(main())

@app.command()
def batch_demo(
    queries_file: str = typer.Argument(..., help="包含查询列表的JSON文件"),
    output_file: str = typer.Option("results.json", help="结果输出文件")
):
    """
    批量运行多个市场分析查询
    
    从文件读取查询列表，批量执行分析并保存结果。
    """
    
    async def batch_main():
        demo = DemoOrchestrator()
        await demo.initialize_system()
        
        try:
            # 读取查询文件
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            
            results = []
            
            console.print(f"📋 开始批量处理 {len(queries)} 个查询...")
            
            for i, query in enumerate(queries, 1):
                console.print(f"\n🔄 处理查询 {i}/{len(queries)}: {query[:50]}...")
                
                result = await demo.team.analyze_market(query)
                
                if result:
                    results.append({
                        "query": query,
                        "result": {
                            "content": result.content,
                            "confidence": result.confidence,
                            "agent_name": result.agent_name,
                            "metadata": result.metadata,
                            "sources": result.sources
                        },
                        "status": "success"
                    })
                    console.print(f"✅ 查询 {i} 完成", style="green")
                else:
                    results.append({
                        "query": query,
                        "result": None,
                        "status": "failed"
                    })
                    console.print(f"❌ 查询 {i} 失败", style="red")
            
            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n📁 结果已保存到: {output_file}", style="green")
            
            # 显示统计
            success_count = sum(1 for r in results if r["status"] == "success")
            console.print(f"📊 成功: {success_count}/{len(queries)}", style="green")
            
        except Exception as e:
            console.print(f"❌ 批量处理失败: {e}", style="red")
    
    asyncio.run(batch_main())

if __name__ == "__main__":
    app() 