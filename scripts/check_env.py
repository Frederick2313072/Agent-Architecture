#!/usr/bin/env python3
"""
简单的 .env 配置检查工具
快速验证环境配置是否正确
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def check_env_file():
    """检查.env文件配置"""
    
    console.print(
        Panel(
            "[bold blue].env 配置检查工具[/bold blue]",
            subtitle="验证您的环境配置",
            border_style="blue"
        )
    )
    
    # 检查.env文件是否存在
    env_file = Path(".env")
    if not env_file.exists():
        console.print("❌ [red].env 文件不存在[/red]")
        console.print(
            Panel(
                "[yellow]解决方案:[/yellow]\n\n"
                "1. 复制模板文件：[cyan]cp env_template.txt .env[/cyan]\n"
                "2. 编辑文件：[cyan]nano .env[/cyan]\n"
                "3. 填入您的 OpenAI API 密钥",
                title="配置指南",
                border_style="yellow"
            )
        )
        return False
    
    console.print("✅ [green].env 文件存在[/green]")
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 检查关键配置
    table = Table(title="配置检查结果")
    table.add_column("配置项", style="cyan")
    table.add_column("状态", style="white")
    table.add_column("值/说明", style="dim")
    
    # 检查 OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_api_key_here":
        if openai_key.startswith("sk-") or openai_key.startswith("sk-proj-"):
            # 显示密钥格式（隐藏中间部分）
            if len(openai_key) > 8:
                masked_key = f"{openai_key[:8]}***{openai_key[-4:]}"
            else:
                masked_key = "sk-***"
            table.add_row("OPENAI_API_KEY", "✅ 格式正确", masked_key)
        else:
            table.add_row("OPENAI_API_KEY", "⚠️ 格式错误", "应以 sk- 或 sk-proj- 开头")
    else:
        table.add_row("OPENAI_API_KEY", "❌ 未配置", "请填入有效的 API 密钥")
    
    # 检查其他配置
    model = os.getenv("DEFAULT_MODEL", "gpt-4o")
    table.add_row("DEFAULT_MODEL", "✅ 配置", model)
    
    moderation = os.getenv("ENABLE_CONTENT_MODERATION", "true")
    table.add_row("ENABLE_CONTENT_MODERATION", "✅ 配置", moderation)
    
    port = os.getenv("PHOENIX_PORT", "6006")
    table.add_row("PHOENIX_PORT", "✅ 配置", port)
    
    console.print(table)
    
    # 检查API密钥有效性
    if openai_key and (openai_key.startswith("sk-") or openai_key.startswith("sk-proj-")):
        console.print(
            Panel(
                "[green]✅ API 密钥格式正确！[/green]\n\n"
                "[yellow]⚠️ 注意：格式正确不代表密钥有效[/yellow]\n\n"
                "[white]验证有效性:[/white]\n"
                "• 运行 API 测试：[cyan]python simple_test.py[/cyan]\n"
                "• 如果遇到 401 错误，说明密钥无效\n\n"
                "[white]下一步:[/white]\n"
                "• 基础功能测试：[cyan]python simple_test.py[/cyan]\n"
                "• Agent调试：[cyan]python debug_agent.py[/cyan]",
                title="配置检查完成",
                border_style="green"
            )
        )
        return True
    else:
        console.print(
            Panel(
                "[red]❌ 需要配置有效的 OpenAI API 密钥[/red]\n\n"
                "[white]获取新的API密钥:[/white]\n"
                "1. 访问：[link]https://platform.openai.com/api-keys[/link]\n"
                "2. 点击 [bold]Create new secret key[/bold]\n"
                "3. 复制完整密钥（sk-... 或 sk-proj-...）\n"
                "4. 在 .env 文件中更新：\n"
                "   [cyan]OPENAI_API_KEY=你的新密钥[/cyan]\n\n"
                "[yellow]💡 提示：确保账户有余额且密钥权限正确[/yellow]",
                title="配置指南",
                border_style="red"
            )
        )
        return False

def main():
    """主函数"""
    success = check_env_file()
    
    if success:
        console.print("\n🎉 [bold green]环境配置检查完成！[/bold green]")
    else:
        console.print("\n⚠️ [bold yellow]请完成配置后重新检查[/bold yellow]")

if __name__ == "__main__":
    main() 