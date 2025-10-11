"""工具函数模块"""

import time
from typing import Dict, Optional, Tuple

import requests
from rich.console import Console

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()


def test_registry_speed(registry_url: str, timeout: int = 5) -> Tuple[bool, Optional[float]]:
    """
    测试镜像源速度
    
    Args:
        registry_url: 镜像源 URL
        timeout: 超时时间（秒）
        
    Returns:
        (是否成功, 响应时间（毫秒）)
    """
    try:
        start_time = time.time()
        response = requests.get(
            registry_url,
            timeout=(timeout, timeout),  # (连接超时, 读取超时) 元组形式
            headers={
                "User-Agent": "pip/23.0 pyrm/0.1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            allow_redirects=True,
            verify=False,  # 避免 SSL 证书验证问题
        )
        elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒

        # 接受 2xx 和 3xx 状态码
        if 200 <= response.status_code < 400:
            return True, elapsed_time
        else:
            return False, None
    except requests.RequestException as e:
        # 打印错误信息用于调试（可选）
        # console.print(f"[dim]Error testing {registry_url}: {str(e)}[/dim]")
        return False, None
    except Exception:
        return False, None


def test_all_registries(
    registries: Dict, timeout: int = 5, verbose: bool = False
) -> Dict[str, Tuple[bool, Optional[float]]]:
    """
    测试所有镜像源的速度
    
    Args:
        registries: 镜像源字典
        timeout: 超时时间（秒）
        verbose: 是否显示详细信息
        
    Returns:
        测试结果字典 {名称: (是否成功, 响应时间)}
    """
    results = {}
    
    with console.status("[bold green]正在测试镜像源速度...") as status:
        for name, info in registries.items():
            status.update(f"[bold green]测试 {name}...")
            url = info["url"]
            success, speed = test_registry_speed(url, timeout)
            results[name] = (success, speed)
            
            if verbose:
                if success:
                    console.print(f"[dim]✓ {name}: {speed:.0f}ms[/dim]")
                else:
                    console.print(f"[dim]✗ {name}: 超时或失败[/dim]")
    
    return results


def format_speed(speed: Optional[float]) -> str:
    """
    格式化速度显示
    
    Args:
        speed: 响应时间（毫秒）
        
    Returns:
        格式化的速度字符串
    """
    if speed is None:
        return "超时"
    elif speed < 100:
        return f"[green]{speed:.0f}ms[/green]"
    elif speed < 500:
        return f"[yellow]{speed:.0f}ms[/yellow]"
    else:
        return f"[red]{speed:.0f}ms[/red]"


def format_registry_name(name: str, is_current: bool = False, is_builtin: bool = True) -> str:
    """
    格式化镜像源名称显示
    
    Args:
        name: 镜像源名称
        is_current: 是否为当前使用的镜像源
        is_builtin: 是否为内置镜像源
        
    Returns:
        格式化的名称字符串
    """
    prefix = "* " if is_current else "  "
    suffix = "" if is_builtin else " [dim](自定义)[/dim]"
    
    if is_current:
        return f"{prefix}[bold green]{name}[/bold green]{suffix}"
    else:
        return f"{prefix}[cyan]{name}[/cyan]{suffix}"


def validate_url(url: str) -> bool:
    """
    验证 URL 格式
    
    Args:
        url: 待验证的 URL
        
    Returns:
        是否为有效 URL
    """
    if not url:
        return False
    
    # 基本的 URL 格式检查
    if not (url.startswith("http://") or url.startswith("https://")):
        return False
    
    # 确保 URL 包含域名
    if len(url.split("/")) < 3:
        return False
    
    return True


def get_registry_by_url(registries: Dict, url: str) -> Optional[str]:
    """
    根据 URL 查找镜像源名称
    
    Args:
        registries: 镜像源字典
        url: 镜像源 URL
        
    Returns:
        镜像源名称，如果未找到则返回 None
    """
    # 移除 URL 末尾的斜杠进行比较
    url = url.rstrip("/")
    
    for name, info in registries.items():
        registry_url = info["url"].rstrip("/")
        if registry_url == url:
            return name
    
    return None

