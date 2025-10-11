"""CLI 主程序入口"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from pyrm.config import PipConfig
from pyrm.registry import RegistryManager
from pyrm.utils import (
    format_registry_name,
    format_speed,
    get_registry_by_url,
    test_all_registries,
    validate_url,
)

app = typer.Typer(
    name="pyrm",
    help="Python pip 镜像源管理工具，类似 nrm",
    add_completion=False,
)

console = Console()
registry_manager = RegistryManager()
pip_config = PipConfig()


@app.command("ls")
def list_registries(
    test: bool = typer.Option(False, "--test", "-t", help="测试所有镜像源速度")
):
    """列出所有可用的镜像源"""
    registries = registry_manager.get_all_registries()
    current_url = pip_config.get_current_registry()
    current_name = get_registry_by_url(registries, current_url) if current_url else None

    # 如果需要测试速度
    speed_results = None
    if test:
        speed_results = test_all_registries(registries)

    # 创建表格
    table = Table(title="📦 可用的 pip 镜像源", show_header=True, header_style="bold magenta")
    table.add_column("", width=2)
    table.add_column("名称", style="cyan")
    table.add_column("URL", style="blue")
    
    if test:
        table.add_column("速度", justify="right")

    # 添加数据
    for name, info in registries.items():
        is_current = name == current_name
        is_builtin = registry_manager.is_builtin(name)
        
        prefix = "*" if is_current else ""
        name_display = name
        if not is_builtin:
            name_display += " (自定义)"
        if is_current:
            name_display = f"[bold green]{name_display}[/bold green]"

        row = [prefix, name_display, info["url"]]
        
        if test and speed_results:
            success, speed = speed_results.get(name, (False, None))
            row.append(format_speed(speed))
        
        table.add_row(*row)

    console.print(table)
    
    if current_name:
        console.print(f"\n✓ 当前使用: [bold green]{current_name}[/bold green]")
    else:
        console.print("\n⚠ 未配置镜像源（使用 pip 默认配置）")


@app.command("use")
def use_registry(
    name: str = typer.Argument(..., help="镜像源名称"),
    scope: str = typer.Option("user", "--scope", "-s", help="配置级别: user, global, local(需要虚拟环境)"),
):
    """切换到指定的镜像源"""
    # 如果是 local 级别，检查虚拟环境
    if scope == "local" and not pip_config.is_in_virtualenv():
        console.print("[red]错误: local 配置级别需要在虚拟环境中使用[/red]")
        console.print("\n请先激活虚拟环境，或使用 [cyan]pyrm use {name}[/cyan] 设置用户级镜像源。")
        console.print("也可以使用 [cyan]pyrm local {name}[/cyan] 命令（会自动检查虚拟环境）。")
        raise typer.Exit(1)
    
    # 检查镜像源是否存在
    registry = registry_manager.get_registry(name)
    if not registry:
        console.print(f"[red]错误: 镜像源 '{name}' 不存在[/red]")
        console.print("使用 [cyan]pyrm ls[/cyan] 查看所有可用的镜像源")
        raise typer.Exit(1)

    # 设置镜像源
    try:
        if pip_config.set_registry(registry["url"], scope=scope):
            scope_text = {
                "user": "用户级",
                "global": "全局",
                "local": "虚拟环境级"
            }.get(scope, scope)
            
            console.print(f"✓ 成功切换到 [bold green]{name}[/bold green] ({scope_text})")
            console.print(f"  URL: {registry['url']}")
            
            if scope == "local":
                config_path = pip_config.get_config_path("local")
                venv_path = pip_config.get_virtualenv_path()
                console.print(f"  配置文件: {config_path}")
                console.print(f"  虚拟环境: {venv_path}")
        else:
            console.print(f"[red]错误: 切换镜像源失败[/red]")
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)


@app.command("current")
def show_current(
    scope: str = typer.Option("user", "--scope", "-s", help="配置级别: user, global, local"),
):
    """显示当前使用的镜像源"""
    scope_text = {
        "user": "用户级",
        "global": "全局",
        "local": "虚拟环境级"
    }.get(scope, scope)
    
    # 如果是 local 级别，检查虚拟环境
    if scope == "local" and not pip_config.is_in_virtualenv():
        console.print(f"[yellow]警告: {scope_text} 配置需要在虚拟环境中使用[/yellow]")
        console.print("当前未检测到虚拟环境\n")
        return
    
    try:
        current_url = pip_config.get_current_registry(scope=scope)
        
        if current_url:
            registries = registry_manager.get_all_registries()
            current_name = get_registry_by_url(registries, current_url)
            
            if current_name:
                registry = registries[current_name]
                console.print(f"✓ 当前 {scope_text} 镜像源: [bold green]{current_name}[/bold green]")
                console.print(f"  URL: {registry['url']}")
                if registry.get("description"):
                    console.print(f"  描述: {registry['description']}")
            else:
                console.print(f"✓ 当前 {scope_text} 镜像源: [yellow]{current_url}[/yellow]")
                console.print("  (未在 pyrm 管理的镜像源列表中)")
        else:
            console.print(f"⚠ {scope_text} 未配置镜像源")
        
        config_path = pip_config.get_config_path(scope)
        console.print(f"\n配置文件: {config_path}")
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")


@app.command("test")
def test_registries(
    timeout: int = typer.Option(3, "--timeout", "-t", help="超时时间（秒）"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细信息"),
):
    """测试所有镜像源的速度"""
    registries = registry_manager.get_all_registries()
    
    if verbose:
        console.print(f"[dim]测试 {len(registries)} 个镜像源，超时时间: {timeout}秒[/dim]\n")
    
    results = test_all_registries(registries, timeout=timeout, verbose=verbose)

    # 按速度排序
    sorted_results = sorted(
        results.items(),
        key=lambda x: (x[1][1] is None, x[1][1] or float('inf'))
    )

    # 创建表格
    table = Table(title="🚀 镜像源速度测试", show_header=True, header_style="bold magenta")
    table.add_column("排名", justify="right", width=6)
    table.add_column("名称", style="cyan")
    table.add_column("URL", style="blue")
    table.add_column("速度", justify="right")

    rank = 1
    for name, (success, speed) in sorted_results:
        registry = registries[name]
        rank_display = str(rank) if success else "-"
        table.add_row(
            rank_display,
            name,
            registry["url"],
            format_speed(speed)
        )
        if success:
            rank += 1

    console.print(table)


@app.command("add")
def add_registry(
    name: str = typer.Argument(..., help="镜像源名称"),
    url: str = typer.Argument(..., help="镜像源 URL"),
    home: str = typer.Option("", "--home", help="主页 URL"),
    description: str = typer.Option("", "--desc", "-d", help="描述"),
):
    """添加自定义镜像源"""
    # 验证 URL 格式
    if not validate_url(url):
        console.print("[red]错误: 无效的 URL 格式[/red]")
        console.print("URL 必须以 http:// 或 https:// 开头")
        raise typer.Exit(1)

    # 检查名称是否已存在
    if registry_manager.get_registry(name):
        if registry_manager.is_builtin(name):
            console.print(f"[red]错误: '{name}' 是内置镜像源，不能覆盖[/red]")
            raise typer.Exit(1)
        else:
            console.print(f"[yellow]警告: 镜像源 '{name}' 已存在，将被覆盖[/yellow]")

    # 添加镜像源
    if registry_manager.add_registry(name, url, home, description):
        console.print(f"✓ 成功添加镜像源 [bold green]{name}[/bold green]")
        console.print(f"  URL: {url}")
        if description:
            console.print(f"  描述: {description}")
    else:
        console.print(f"[red]错误: 添加镜像源失败[/red]")
        raise typer.Exit(1)


@app.command("del")
def delete_registry(
    name: str = typer.Argument(..., help="镜像源名称"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不需要确认"),
):
    """删除自定义镜像源"""
    # 检查是否为内置镜像源
    if registry_manager.is_builtin(name):
        console.print(f"[red]错误: '{name}' 是内置镜像源，不能删除[/red]")
        raise typer.Exit(1)

    # 检查镜像源是否存在
    registry = registry_manager.get_registry(name)
    if not registry:
        console.print(f"[red]错误: 镜像源 '{name}' 不存在[/red]")
        raise typer.Exit(1)

    # 确认删除
    if not force:
        confirm = typer.confirm(f"确定要删除镜像源 '{name}' 吗?")
        if not confirm:
            console.print("已取消")
            raise typer.Exit(0)

    # 删除镜像源
    if registry_manager.delete_registry(name):
        console.print(f"✓ 成功删除镜像源 [bold green]{name}[/bold green]")
    else:
        console.print(f"[red]错误: 删除镜像源失败[/red]")
        raise typer.Exit(1)


@app.command("local")
def set_local_registry(
    name: Optional[str] = typer.Argument(None, help="镜像源名称，留空则显示当前虚拟环境镜像源"),
    project_dir: Optional[Path] = typer.Option(None, "--dir", "-d", help="（保留参数，实际未使用）"),
):
    """为当前虚拟环境设置镜像源
    
    注意：此命令需要在激活的虚拟环境中使用。
    pip 只支持虚拟环境级别的配置，不支持项目目录下的配置文件。
    
    示例：
        # 先激活虚拟环境
        source venv/bin/activate
        
        # 为虚拟环境设置镜像源
        pyrm local tsinghua
    """
    # 检查是否在虚拟环境中
    if not pip_config.is_in_virtualenv():
        console.print("[red]错误: 未检测到虚拟环境[/red]")
        console.print("\n此命令需要在虚拟环境中使用。pip 只支持虚拟环境级别的配置。\n")
        console.print("请先创建并激活虚拟环境：")
        console.print("  [cyan]python -m venv venv[/cyan]                # 创建虚拟环境")
        console.print("  [cyan]source venv/bin/activate[/cyan]           # Linux/macOS 激活")
        console.print("  [cyan]venv\\Scripts\\activate[/cyan]              # Windows 激活")
        console.print("\n然后再运行此命令，或使用 [cyan]pyrm use <name>[/cyan] 设置用户级镜像源。")
        raise typer.Exit(1)
    
    if name is None:
        # 显示当前虚拟环境的镜像源
        try:
            show_current(scope="local")
            venv_path = pip_config.get_virtualenv_path()
            console.print(f"\n💡 虚拟环境路径: {venv_path}")
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")
            raise typer.Exit(1)
        return

    # 检查镜像源是否存在
    registry = registry_manager.get_registry(name)
    if not registry:
        console.print(f"[red]错误: 镜像源 '{name}' 不存在[/red]")
        console.print("使用 [cyan]pyrm ls[/cyan] 查看所有可用的镜像源")
        raise typer.Exit(1)

    # 设置虚拟环境级镜像源
    try:
        if pip_config.set_registry(registry["url"], scope="local"):
            config_path = pip_config.get_config_path("local")
            venv_path = pip_config.get_virtualenv_path()
            
            console.print(f"✓ 成功为当前虚拟环境设置镜像源 [bold green]{name}[/bold green]")
            console.print(f"  URL: {registry['url']}")
            console.print(f"  配置文件: {config_path}")
            console.print(f"  虚拟环境: {venv_path}")
            console.print(f"\n💡 在此虚拟环境中使用 pip 时将自动使用此镜像源")
        else:
            console.print(f"[red]错误: 设置虚拟环境镜像源失败[/red]")
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)


@app.command("edit")
def edit_config(
    scope: str = typer.Option("user", "--scope", "-s", help="配置级别: user, global, local"),
):
    """可视化编辑 pip 配置文件"""
    try:
        from pyrm.editor import run_editor
        
        config_path = pip_config.get_config_path(scope)
        run_editor(config_path, scope)
    except ImportError:
        console.print("[red]错误: 可视化编辑器依赖未安装[/red]")
        console.print("请安装 textual: pip install textual")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)


@app.command("version")
def show_version():
    """显示版本信息"""
    from pyrm import __version__
    console.print(f"pyrm version [bold green]{__version__}[/bold green]")
    console.print("Python pip 镜像源管理工具")


def main():
    """主入口函数"""
    app()


if __name__ == "__main__":
    main()

