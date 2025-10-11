"""测试工具函数模块"""

import pytest

from pyrm.utils import (
    format_registry_name,
    format_speed,
    get_registry_by_url,
    validate_url,
)


def test_validate_url():
    """测试 URL 验证"""
    # 有效的 URL
    assert validate_url("https://pypi.org/simple") is True
    assert validate_url("http://example.com/pypi/simple") is True
    
    # 无效的 URL
    assert validate_url("") is False
    assert validate_url("not-a-url") is False
    assert validate_url("ftp://example.com") is False
    assert validate_url("https://") is False


def test_format_speed():
    """测试速度格式化"""
    # 测试不同速度范围
    result = format_speed(50)
    assert "50" in result
    assert "ms" in result
    
    result = format_speed(200)
    assert "200" in result
    
    result = format_speed(600)
    assert "600" in result
    
    result = format_speed(None)
    assert "超时" in result


def test_format_registry_name():
    """测试镜像源名称格式化"""
    # 当前使用的内置镜像源
    result = format_registry_name("pypi", is_current=True, is_builtin=True)
    assert "pypi" in result
    assert "*" in result
    
    # 非当前的内置镜像源
    result = format_registry_name("tsinghua", is_current=False, is_builtin=True)
    assert "tsinghua" in result
    
    # 自定义镜像源
    result = format_registry_name("custom", is_current=False, is_builtin=False)
    assert "custom" in result
    assert "自定义" in result


def test_get_registry_by_url():
    """测试根据 URL 查找镜像源"""
    test_registries = {
        "pypi": {
            "name": "pypi",
            "url": "https://pypi.org/simple",
        },
        "tsinghua": {
            "name": "tsinghua",
            "url": "https://pypi.tuna.tsinghua.edu.cn/simple",
        },
    }
    
    # 查找存在的镜像源
    name = get_registry_by_url(test_registries, "https://pypi.org/simple")
    assert name == "pypi"
    
    # URL 末尾有斜杠也应该能找到
    name = get_registry_by_url(test_registries, "https://pypi.org/simple/")
    assert name == "pypi"
    
    # 查找不存在的镜像源
    name = get_registry_by_url(test_registries, "https://nonexistent.com/simple")
    assert name is None

