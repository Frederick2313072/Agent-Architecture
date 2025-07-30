#!/usr/bin/env python3
"""
Phoenix UI 诊断和修复工具
专门解决 Phoenix 可观测性界面无法访问的问题
"""

import os
import sys
import subprocess
import socket
import time
import requests
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

console = Console()

def check_port_available(port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # 0 表示端口被占用
    except Exception:
        return True

def check_process_on_port(port: int) -> str:
    """检查占用端口的进程"""
    try:
        # macOS/Linux
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True, timeout=5)
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # 忽略表头
                return lines[1].split()[0]  # 返回进程名
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        try:
            # Windows
            result = subprocess.run(['netstat', '-ano', '|', 'findstr', f':{port}'], 
                                  shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                return "Unknown Process"
        except:
            pass
    return "Unknown"

def test_phoenix_import():
    """测试 Phoenix 库导入"""
    try:
        import phoenix as px
        console.print("✅ [green]Phoenix 库导入成功[/green]")
        
        # 检查版本
        try:
            version = px.__version__
            console.print(f"📦 [blue]Phoenix 版本: {version}[/blue]")
        except:
            console.print("📦 [yellow]无法获取 Phoenix 版本[/yellow]")
        
        return True, px
    except ImportError as e:
        console.print(f"❌ [red]Phoenix 库导入失败: {e}[/red]")
        console.print("💡 [yellow]请安装: pip install arize-phoenix[/yellow]")
        return False, None

def test_phoenix_startup(port: int = 6006):
    """测试 Phoenix 启动"""
    
    console.print(f"🚀 [blue]尝试在端口 {port} 启动 Phoenix...[/blue]")
    
    success, px = test_phoenix_import()
    if not success:
        return False, None
    
    try:
        # 检查端口可用性
        if not check_port_available(port):
            process = check_process_on_port(port)
            console.print(f"⚠️ [yellow]端口 {port} 已被占用 (进程: {process})[/yellow]")
            
            # 建议替代端口
            for alt_port in [6007, 6008, 6009, 7006, 8006]:
                if check_port_available(alt_port):
                    console.print(f"💡 [cyan]建议使用端口 {alt_port}[/cyan]")
                    port = alt_port
                    break
            else:
                console.print("❌ [red]没有找到可用端口[/red]")
                return False, None
        
        # 设置 Phoenix 环境变量（新的推荐方式）
        import os
        os.environ["PHOENIX_PORT"] = str(port)
        os.environ["PHOENIX_HOST"] = "localhost"
        
        # 启动 Phoenix（使用新的无参数方式）
        session = px.launch_app()
        
        # 等待启动
        time.sleep(3)
        
        # 验证服务是否响应
        try:
            response = requests.get(f"http://localhost:{port}", timeout=5)
            if response.status_code == 200:
                console.print(f"✅ [green]Phoenix UI 启动成功: http://localhost:{port}[/green]")
                return True, session
            else:
                console.print(f"⚠️ [yellow]Phoenix 启动但响应异常 (状态码: {response.status_code})[/yellow]")
                return False, session
        except requests.RequestException as e:
            console.print(f"⚠️ [yellow]Phoenix 启动但无法连接: {e}[/yellow]")
            return False, session
            
    except Exception as e:
        console.print(f"❌ [red]Phoenix 启动失败: {e}[/red]")
        return False, None

def diagnose_phoenix():
    """全面诊断 Phoenix 问题"""
    
    console.print(
        Panel(
            "[bold blue]Phoenix UI 诊断工具[/bold blue]",
            subtitle="诊断可观测性界面访问问题",
            border_style="blue"
        )
    )
    
    # 创建诊断表格
    table = Table(title="Phoenix 诊断结果")
    table.add_column("检查项目", style="cyan")
    table.add_column("状态", style="white")
    table.add_column("详情", style="dim")
    
    # 1. 检查 Phoenix 库
    success, px = test_phoenix_import()
    if success:
        table.add_row("Phoenix 库", "✅ 正常", "库导入成功")
    else:
        table.add_row("Phoenix 库", "❌ 失败", "需要安装")
        console.print(table)
        return False
    
    # 2. 检查默认端口
    default_port = int(os.getenv("PHOENIX_PORT", "6006"))
    port_available = check_port_available(default_port)
    
    if port_available:
        table.add_row(f"端口 {default_port}", "✅ 可用", "端口未被占用")
    else:
        process = check_process_on_port(default_port)
        table.add_row(f"端口 {default_port}", "❌ 占用", f"被进程占用: {process}")
    
    # 3. 检查 OTLP 端口
    otlp_main_port = 4317
    otlp_fallback_port = int(os.getenv("OTEL_FALLBACK_PORT", "4318"))
    
    otlp_main_available = check_port_available(otlp_main_port)
    otlp_fallback_available = check_port_available(otlp_fallback_port)
    
    if otlp_main_available:
        table.add_row(f"OTLP 端口 {otlp_main_port}", "✅ 可用", "主 GRPC 端口可用")
    elif otlp_fallback_available:
        table.add_row(f"OTLP 端口 {otlp_main_port}", "⚠️ 占用", f"备用端口 {otlp_fallback_port} 可用")
    else:
        table.add_row(f"OTLP 端口 {otlp_main_port}", "❌ 冲突", f"主端口和备用端口 {otlp_fallback_port} 都被占用")
    
    # 4. 检查网络连接
    try:
        response = requests.get("http://localhost", timeout=2)
        table.add_row("本地网络", "✅ 正常", "localhost 可访问")
    except:
        table.add_row("本地网络", "⚠️ 异常", "localhost 连接问题")
    
    console.print(table)
    
    # 5. 尝试启动测试
    console.print("\n" + "="*50)
    console.print("[bold]Phoenix 启动测试[/bold]")
    
    success, session = test_phoenix_startup(default_port if port_available else 6007)
    
    return success, session

def provide_solutions():
    """提供解决方案"""
    
    console.print(
        Panel(
            "[bold yellow]Phoenix UI 问题解决方案[/bold yellow]\n\n"
            
            "[white]方案 1: 安装/重新安装 Phoenix[/white]\n"
            "[cyan]pip install -U arize-phoenix[/cyan]\n\n"
            
            "[white]方案 2: 使用不同端口[/white]\n"
            "[cyan]export PHOENIX_PORT=6007[/cyan]\n"
            "[cyan]python demo.py run-demo \"测试\"[/cyan]\n\n"
            
            "[white]方案 3: 手动启动 Phoenix[/white]\n"
            "[cyan]PHOENIX_PORT=6007 python -c \"import phoenix as px; px.launch_app()\"[/cyan]\n\n"
            
            "[white]方案 4: 解决 GRPC 端口冲突[/white]\n"
            "[cyan]export OTEL_FALLBACK_PORT=4318[/cyan]\n"
            "[cyan]export ENABLE_GRPC_FALLBACK=true[/cyan]\n\n"
            
            "[white]方案 5: 禁用 OTLP 导出 (仅本地追踪)[/white]\n"
            "[cyan]export ENABLE_GRPC_FALLBACK=false[/cyan]\n\n"
            
            "[white]方案 6: 禁用 Phoenix (仅使用日志)[/white]\n"
            "[cyan]export ENABLE_TRACING=false[/cyan]\n"
            "[cyan]python demo.py run-demo \"测试\"[/cyan]\n\n"
            
            "[white]方案 7: 检查防火墙设置[/white]\n"
            "确保防火墙允许本地端口访问",
            title="解决方案",
            border_style="yellow"
        )
    )

def main():
    """主函数"""
    
    console.print("""
[bold blue]🔍 Phoenix UI 诊断工具[/bold blue]

专门诊断 Phoenix 可观测性界面无法访问的问题：
• 检查 Phoenix 库安装状态
• 验证 Phoenix UI 端口可用性
• 检查 OTLP/GRPC 端口冲突
• 测试服务启动
• 提供解决方案
""")
    
    try:
        # 运行诊断
        success, session = diagnose_phoenix()
        
        console.print("\n" + "="*50)
        
        if success:
            console.print(
                Panel(
                    "[bold green]🎉 Phoenix UI 诊断通过！[/bold green]\n\n"
                    "[white]可以正常使用可观测性功能。[/white]\n"
                    "[white]现在可以运行完整演示：[/white]\n"
                    "[cyan]python demo.py run-demo \"您的查询\"[/cyan]",
                    title="诊断成功",
                    border_style="green"
                )
            )
        else:
            console.print(
                Panel(
                    "[bold red]❌ Phoenix UI 存在问题[/bold red]\n\n"
                    "[white]请参考下面的解决方案。[/white]",
                    title="诊断失败",
                    border_style="red"
                )
            )
            provide_solutions()
            
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]诊断已取消[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [red]诊断过程出错: {e}[/red]")
        provide_solutions()

if __name__ == "__main__":
    main() 