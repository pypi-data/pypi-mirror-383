"""测试镜像源管理模块"""

import tempfile
from pathlib import Path

import pytest

from pyrm.registry import BUILTIN_REGISTRIES, RegistryManager


def test_builtin_registries():
    """测试内置镜像源"""
    assert "pypi" in BUILTIN_REGISTRIES
    assert "tsinghua" in BUILTIN_REGISTRIES
    assert "aliyun" in BUILTIN_REGISTRIES
    
    pypi = BUILTIN_REGISTRIES["pypi"]
    assert "url" in pypi
    assert "name" in pypi
    assert "description" in pypi


def test_registry_manager_init():
    """测试 RegistryManager 初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = RegistryManager(config_dir=config_dir)
        
        assert manager.config_dir == config_dir
        assert manager.config_dir.exists()


def test_get_all_registries():
    """测试获取所有镜像源"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RegistryManager(config_dir=Path(tmpdir))
        registries = manager.get_all_registries()
        
        # 至少包含内置镜像源
        assert len(registries) >= len(BUILTIN_REGISTRIES)
        assert "pypi" in registries
        assert "tsinghua" in registries


def test_get_registry():
    """测试获取单个镜像源"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RegistryManager(config_dir=Path(tmpdir))
        
        # 获取内置镜像源
        pypi = manager.get_registry("pypi")
        assert pypi is not None
        assert pypi["name"] == "pypi"
        
        # 获取不存在的镜像源
        nonexistent = manager.get_registry("nonexistent")
        assert nonexistent is None


def test_add_registry():
    """测试添加自定义镜像源"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RegistryManager(config_dir=Path(tmpdir))
        
        # 添加自定义镜像源
        success = manager.add_registry(
            "custom",
            "https://custom.com/simple",
            "https://custom.com",
            "Custom Registry"
        )
        assert success is True
        
        # 验证添加成功
        custom = manager.get_registry("custom")
        assert custom is not None
        assert custom["name"] == "custom"
        assert custom["url"] == "https://custom.com/simple"
        
        # 尝试覆盖内置镜像源（应该失败）
        success = manager.add_registry("pypi", "https://fake.com/simple")
        assert success is False


def test_delete_registry():
    """测试删除自定义镜像源"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RegistryManager(config_dir=Path(tmpdir))
        
        # 添加自定义镜像源
        manager.add_registry("custom", "https://custom.com/simple")
        
        # 删除自定义镜像源
        success = manager.delete_registry("custom")
        assert success is True
        
        # 验证删除成功
        custom = manager.get_registry("custom")
        assert custom is None
        
        # 尝试删除内置镜像源（应该失败）
        success = manager.delete_registry("pypi")
        assert success is False
        
        # 尝试删除不存在的镜像源（应该失败）
        success = manager.delete_registry("nonexistent")
        assert success is False


def test_is_builtin():
    """测试判断是否为内置镜像源"""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = RegistryManager(config_dir=Path(tmpdir))
        
        assert manager.is_builtin("pypi") is True
        assert manager.is_builtin("tsinghua") is True
        assert manager.is_builtin("nonexistent") is False
        
        # 添加自定义镜像源
        manager.add_registry("custom", "https://custom.com/simple")
        assert manager.is_builtin("custom") is False

