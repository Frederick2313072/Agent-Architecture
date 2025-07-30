#!/usr/bin/env python3
"""
完整的 Agent 系统 Tracing 指南
演示如何在各个层面进行追踪和可观测性
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from src.observability import ObservabilityManager, traced_agent_operation, log_conversation
from src.safety import SafetyManager, ValidationStatus
from src.config import config

console = Console()

class TracingDemoAgent:
    """演示 Tracing 功能的示例 Agent"""
    
    def __init__(self, name: str):
        self.name = name
        self.obs_manager = ObservabilityManager()
        self.safety_manager = SafetyManager()
        
    @traced_agent_operation("agent_initialization")
    def initialize(self):
        """初始化 Agent"""
        console.print(f"🤖 [blue]初始化 Agent: {self.name}[/blue]")
        self.obs_manager.initialize()
        return f"Agent {self.name} 初始化完成"
    
    @traced_agent_operation("agent_thinking")
    def think(self, input_message: str) -> Dict[str, Any]:
        """Agent 思考过程"""
        console.print(f"🧠 [yellow]{self.name} 正在思考: {input_message[:50]}...[/yellow]")
        
        # 模拟思考时间
        time.sleep(0.5)
        
        thought_process = {
            "original_input": input_message,
            "analysis": f"分析输入内容的主要意图和关键词",
            "strategy": "选择最适合的回应策略",
            "confidence": 0.85,
            "reasoning_steps": [
                "1. 解析用户意图",
                "2. 检索相关知识",
                "3. 构建回应框架",
                "4. 优化表达方式"
            ]
        }
        
        return thought_process
    
    @traced_agent_operation("agent_generate_reply")
    async def generate_reply(self, messages: List[Dict], context: Dict = None) -> str:
        """生成回复 - 包含完整的 tracing"""
        console.print(f"💬 [green]{self.name} 正在生成回复...[/green]")
        
        # 记录对话到追踪系统
        log_conversation(
            agent_name=self.name,
            message=str(messages),
            role="user",
            metadata={"context": context or {}}
        )
        
        # 1. 安全检查
        input_content = messages[-1].get("content", "") if messages else ""
        safety_result = await self.safety_manager.moderate_content(input_content)
        
        if safety_result.flagged:
            console.print(f"⚠️ [red]内容被安全检查标记: {safety_result.reason}[/red]")
            return "抱歉，我无法处理这个请求。"
        
        # 2. 思考过程
        thought = self.think(input_content)
        
        # 3. 生成回复
        reply = f"基于分析，我认为：{input_content[:30]}... 的最佳回应是通过{thought['strategy']}来处理。"
        
        # 4. 输出验证
        validation_status, validated_output = self.safety_manager.validate_agent_output(
            reply, self.name
        )
        
        if validation_status != ValidationStatus.VALID:
            console.print(f"⚠️ [yellow]输出验证状态: {validation_status}[/yellow]")
        
        # 记录生成的回复
        log_conversation(
            agent_name=self.name,
            message=reply,
            role="assistant",
            metadata={
                "thought_process": thought,
                "safety_check": safety_result.flagged,
                "validation_status": validation_status.value
            }
        )
        
        return reply

class TracingWorkflowDemo:
    """Tracing 工作流演示"""
    
    def __init__(self):
        self.agents = {
            "researcher": TracingDemoAgent("市场研究员"),
            "analyst": TracingDemoAgent("数据分析师"), 
            "writer": TracingDemoAgent("报告撰写员")
        }
        
    @traced_agent_operation("workflow_execution")
    async def run_workflow(self, query: str) -> Dict[str, Any]:
        """运行完整的多Agent工作流"""
        console.print(Panel(f"🚀 启动工作流: {query}", style="blue"))
        
        workflow_results = {}
        
        # 阶段1：初始化所有Agents
        console.print("\n📋 [cyan]阶段1: Agent初始化[/cyan]")
        for agent_name, agent in self.agents.items():
            result = agent.initialize()
            workflow_results[f"{agent_name}_init"] = result
        
        # 阶段2：研究阶段
        console.print("\n🔍 [cyan]阶段2: 市场研究[/cyan]")
        research_messages = [{"role": "user", "content": f"请研究以下主题: {query}"}]
        research_result = await self.agents["researcher"].generate_reply(
            research_messages, 
            {"phase": "research", "query": query}
        )
        workflow_results["research"] = research_result
        
        # 阶段3：数据分析
        console.print("\n📊 [cyan]阶段3: 数据分析[/cyan]")
        analysis_messages = [
            {"role": "user", "content": f"基于研究结果进行数据分析: {research_result[:100]}..."}
        ]
        analysis_result = await self.agents["analyst"].generate_reply(
            analysis_messages,
            {"phase": "analysis", "research_input": research_result}
        )
        workflow_results["analysis"] = analysis_result
        
        # 阶段4：报告撰写
        console.print("\n📝 [cyan]阶段4: 报告撰写[/cyan]")
        writing_messages = [
            {"role": "user", "content": f"撰写综合报告，整合研究和分析结果"}
        ]
        final_report = await self.agents["writer"].generate_reply(
            writing_messages,
            {
                "phase": "writing", 
                "research_input": research_result,
                "analysis_input": analysis_result
            }
        )
        workflow_results["final_report"] = final_report
        
        return workflow_results

@traced_agent_operation("performance_monitoring")
def monitor_system_performance():
    """监控系统性能指标"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "system_load": "模拟: 65%",
        "memory_usage": "模拟: 2.1GB", 
        "active_agents": 3,
        "total_traces": "129",  # 从您的截图中看到的数据
        "avg_latency": "7.63s",  # P50延迟
        "p99_latency": "33.35s"  # P99延迟
    }
    
    table = Table(title="系统性能监控")
    table.add_column("指标", style="cyan")
    table.add_column("当前值", style="green")
    
    for metric, value in metrics.items():
        table.add_row(metric, str(value))
    
    console.print(table)
    return metrics

@traced_agent_operation("trace_analysis")
def analyze_traces():
    """分析追踪数据"""
    console.print(Panel("🔍 Trace 数据分析", style="green"))
    
    # 模拟从Phoenix UI获取的数据
    trace_analysis = {
        "total_spans": 129,
        "span_types": {
            "agent_conversation": 45,
            "content_moderation": 23,
            "output_validation": 31,
            "agent_generate_reply": 18,
            "openai.chat": 8,
            "self_correction_loop": 4
        },
        "latency_distribution": {
            "< 1s": "65%",
            "1-5s": "25%", 
            "5-10s": "8%",
            "> 10s": "2%"
        },
        "error_rate": "0.7%",
        "success_rate": "99.3%"
    }
    
    # 显示分析结果
    spans_table = Table(title="Span 类型分布")
    spans_table.add_column("Span 类型", style="cyan")
    spans_table.add_column("数量", style="yellow")
    
    for span_type, count in trace_analysis["span_types"].items():
        spans_table.add_row(span_type, str(count))
    
    console.print(spans_table)
    
    latency_table = Table(title="延迟分布")
    latency_table.add_column("延迟范围", style="cyan")
    latency_table.add_column("占比", style="green")
    
    for range_name, percentage in trace_analysis["latency_distribution"].items():
        latency_table.add_row(range_name, percentage)
    
    console.print(latency_table)
    
    return trace_analysis

async def main():
    """完整的 Tracing 演示"""
    console.print("🚀 [bold blue]Agent 系统 Tracing 完整演示[/bold blue]\n")
    
    # 1. 性能监控
    monitor_system_performance()
    console.print()
    
    # 2. 运行工作流
    demo = TracingWorkflowDemo()
    
    test_queries = [
        "分析人工智能股票的投资机会",
        "评估新能源汽车市场前景"
    ]
    
    with Progress() as progress:
        task = progress.add_task("执行 Tracing 工作流...", total=len(test_queries))
        
        for query in test_queries:
            console.print(f"\n🎯 [bold yellow]处理查询: {query}[/bold yellow]")
            
            start_time = time.time()
            results = await demo.run_workflow(query)
            duration = time.time() - start_time
            
            console.print(f"✅ [green]工作流完成，耗时: {duration:.2f}秒[/green]")
            progress.update(task, advance=1)
    
    console.print()
    
    # 3. 分析追踪数据
    analyze_traces()
    
    # 4. 显示Phoenix UI访问信息
    phoenix_port = config.observability.phoenix_port
    console.print(Panel(
        f"🌐 访问 Phoenix UI 查看详细追踪数据:\n\n"
        f"URL: http://localhost:{phoenix_port}\n"
        f"页面: Traces -> 查看最新的 span 数据\n"
        f"筛选: 可以按 span 类型、延迟、时间范围等筛选\n\n"
        f"📊 关键指标:\n"
        f"• Total Traces: 查看总追踪数量\n"
        f"• Latency P50/P99: 监控响应时间\n"
        f"• Error Rate: 监控系统健康状态\n"
        f"• Span Details: 查看每个操作的详细信息",
        title="🔍 Phoenix UI 使用指南",
        style="cyan"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 