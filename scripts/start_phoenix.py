#!/usr/bin/env python3
"""
独立的 Phoenix UI 启动工具
快速启动可观测性界面，无需运行完整演示
"""

import os
import sys
import signal
import time
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

console = Console()

def start_phoenix_ui():
    """启动 Phoenix UI"""
    
    console.print(
        Panel(
            "[bold blue]🚀 Phoenix UI 启动器[/bold blue]\n\n"
            "[white]独立启动可观测性界面[/white]\n"
            "[dim]按 Ctrl+C 停止服务[/dim]",
            title="Phoenix 启动器",
            border_style="blue"
        )
    )
    
    try:
        # 导入 Phoenix
        import phoenix as px
        console.print("✅ [green]Phoenix 库加载成功[/green]")
        
        # 获取端口配置
        port = int(os.getenv("PHOENIX_PORT", "6006"))
        console.print(f"📡 [blue]准备在端口 {port} 启动服务...[/blue]")
        
        # 设置 Phoenix 环境变量（新的推荐方式）
        os.environ["PHOENIX_PORT"] = str(port)
        os.environ["PHOENIX_HOST"] = "localhost"
        
        # 启动 Phoenix（使用新的无参数方式）
        session = px.launch_app()
        
        console.print(
            Panel(
                f"[bold green]🎉 Phoenix UI 启动成功！[/bold green]\n\n"
                f"[white]访问地址:[/white] [link]http://localhost:{port}[/link]\n\n"
                f"[white]功能说明:[/white]\n"
                f"• 查看 Agent 对话追踪\n"
                f"• 分析 LLM 调用性能\n"
                f"• 监控系统运行状态\n\n"
                f"[yellow]提示: 现在可以运行 Agent 演示来生成追踪数据[/yellow]",
                title="🌐 Phoenix UI 就绪",
                border_style="green"
            )
        )
        
        console.print(f"[dim]Phoenix 会话 ID: {session}[/dim]")
        console.print("\n[bold yellow]按 Ctrl+C 停止服务[/bold yellow]")
        
        try:
            # 保持服务运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n👋 [yellow]正在停止 Phoenix UI...[/yellow]")
            
    except ImportError:
        console.print(
            Panel(
                "[bold red]❌ Phoenix 库未安装[/bold red]\n\n"
                "[white]安装命令:[/white]\n"
                "[cyan]pip install arize-phoenix[/cyan]\n\n"
                "[white]或者安装完整依赖:[/white]\n"
                "[cyan]pip install -r requirements.txt[/cyan]",
                title="安装错误",
                border_style="red"
            )
        )
        return False
        
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]❌ Phoenix 启动失败[/bold red]\n\n"
                f"[white]错误信息:[/white] {e}\n\n"
                f"[white]可能的解决方案:[/white]\n"
                f"• 检查端口 {port} 是否被占用\n"
                f"• 尝试使用不同端口: [cyan]export PHOENIX_PORT=6007[/cyan]\n"
                f"• 运行诊断工具: [cyan]python check_phoenix.py[/cyan]",
                title="启动错误",
                border_style="red"
            )
        )
        return False
    
    return True

def show_usage():
    """显示使用说明"""
    
    console.print("""
[bold blue]📖 Phoenix UI 使用指南[/bold blue]

[white]基本用法:[/white]
[cyan]python start_phoenix.py[/cyan]    # 启动 Phoenix UI

[white]自定义端口:[/white]
[cyan]export PHOENIX_PORT=6007[/cyan]
[cyan]python start_phoenix.py[/cyan]

[white]或者一次性设置:[/white]
[cyan]PHOENIX_PORT=6007 python start_phoenix.py[/cyan]

[white]结合 Agent 演示使用:[/white]
1. 在终端1中运行: [cyan]python start_phoenix.py[/cyan]
2. 在终端2中运行: [cyan]python demo.py run-demo "您的查询"[/cyan]
3. 在浏览器中查看追踪数据

[white]常见问题:[/white]
• 端口被占用: 运行 [cyan]python check_phoenix.py[/cyan] 诊断
• 无法访问: 检查防火墙设置
• 启动失败: 确认已安装 arize-phoenix 库
""")

def main():
    """主函数"""
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
        return
    
    # 启动 Phoenix UI
    success = start_phoenix_ui()
    
    if not success:
        console.print("\n💡 [cyan]提示: 运行 python check_phoenix.py 进行详细诊断[/cyan]")

if __name__ == "__main__":
    main() 