"""配置管理模块 - 管理 pip 配置文件"""

import configparser
import os
import platform
from pathlib import Path
from typing import Optional


class PipConfig:
    """pip 配置管理器"""

    def __init__(self):
        """初始化 pip 配置管理器"""
        self.system = platform.system()
        self.global_config_path = self._get_global_config_path()
        self.user_config_path = self._get_user_config_path()

    def _get_global_config_path(self) -> Path:
        """获取全局 pip 配置文件路径"""
        if self.system == "Windows":
            return Path("C:/ProgramData/pip/pip.ini")
        else:
            return Path("/etc/pip.conf")

    def _get_user_config_path(self) -> Path:
        """获取用户级 pip 配置文件路径"""
        if self.system == "Windows":
            return Path.home() / "pip" / "pip.ini"
        else:
            # Linux/macOS
            return Path.home() / ".pip" / "pip.conf"

    def _get_local_config_path(self, project_dir: Optional[Path] = None) -> Path:
        """
        获取虚拟环境级 pip 配置文件路径
        
        注意：这里的 "local" 实际指的是虚拟环境配置（site-level），
        而不是项目目录下的配置文件。pip 只支持虚拟环境级别的配置。
        
        Args:
            project_dir: 保留参数以保持兼容性，但实际未使用
            
        Returns:
            虚拟环境配置文件路径
            
        Raises:
            ValueError: 如果未检测到虚拟环境
        """
        # 检测虚拟环境
        virtual_env = os.environ.get('VIRTUAL_ENV')
        
        if not virtual_env:
            raise ValueError(
                "未检测到虚拟环境。\n"
                "请先创建并激活虚拟环境，或使用 user/global 配置级别。\n\n"
                "创建虚拟环境:\n"
                "  python -m venv venv\n"
                "激活虚拟环境:\n"
                "  source venv/bin/activate  # Linux/macOS\n"
                "  venv\\Scripts\\activate     # Windows"
            )
        
        # 返回虚拟环境的配置文件路径
        venv_path = Path(virtual_env)
        
        if self.system == "Windows":
            return venv_path / "pip.ini"
        else:
            return venv_path / "pip.conf"

    def _ensure_config_dir(self, config_path: Path) -> None:
        """确保配置文件目录存在"""
        config_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_config(self, config_path: Path) -> configparser.ConfigParser:
        """
        读取配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            ConfigParser 对象
        """
        config = configparser.ConfigParser()
        if config_path.exists():
            config.read(config_path, encoding="utf-8")
        return config

    def _write_config(self, config: configparser.ConfigParser, config_path: Path) -> None:
        """
        写入配置文件
        
        Args:
            config: ConfigParser 对象
            config_path: 配置文件路径
        """
        self._ensure_config_dir(config_path)
        with open(config_path, "w", encoding="utf-8") as f:
            config.write(f)

    def get_current_registry(self, scope: str = "user") -> Optional[str]:
        """
        获取当前配置的镜像源
        
        Args:
            scope: 配置级别，可选 'user', 'global', 'local'
            
        Returns:
            当前镜像源 URL，如果未配置则返回 None
        """
        if scope == "user":
            config_path = self.user_config_path
        elif scope == "global":
            config_path = self.global_config_path
        elif scope == "local":
            config_path = self._get_local_config_path()
        else:
            config_path = self.user_config_path

        config = self._read_config(config_path)
        
        if config.has_section("global") and config.has_option("global", "index-url"):
            return config.get("global", "index-url")
        return None

    def set_registry(self, registry_url: str, scope: str = "user") -> bool:
        """
        设置镜像源
        
        Args:
            registry_url: 镜像源 URL
            scope: 配置级别，可选 'user', 'global', 'local'
            
        Returns:
            是否设置成功
        """
        try:
            if scope == "user":
                config_path = self.user_config_path
            elif scope == "global":
                config_path = self.global_config_path
            elif scope == "local":
                config_path = self._get_local_config_path()
            else:
                config_path = self.user_config_path

            config = self._read_config(config_path)

            # 确保 global section 存在
            if not config.has_section("global"):
                config.add_section("global")

            # 设置 index-url
            config.set("global", "index-url", registry_url)
            
            # 设置 trusted-host (移除协议和路径，只保留域名)
            from urllib.parse import urlparse
            parsed = urlparse(registry_url)
            if parsed.hostname:
                config.set("global", "trusted-host", parsed.hostname)

            self._write_config(config, config_path)
            return True
        except Exception as e:
            print(f"设置镜像源失败: {e}")
            return False

    def get_all_config(self, scope: str = "user") -> dict:
        """
        获取所有配置
        
        Args:
            scope: 配置级别
            
        Returns:
            配置字典
        """
        if scope == "user":
            config_path = self.user_config_path
        elif scope == "global":
            config_path = self.global_config_path
        elif scope == "local":
            config_path = self._get_local_config_path()
        else:
            config_path = self.user_config_path

        config = self._read_config(config_path)
        result = {}
        
        for section in config.sections():
            result[section] = dict(config.items(section))
        
        return result

    def update_config(self, section: str, option: str, value: str, scope: str = "user") -> bool:
        """
        更新配置项
        
        Args:
            section: 配置段
            option: 配置项
            value: 配置值
            scope: 配置级别
            
        Returns:
            是否更新成功
        """
        try:
            if scope == "user":
                config_path = self.user_config_path
            elif scope == "global":
                config_path = self.global_config_path
            elif scope == "local":
                config_path = self._get_local_config_path()
            else:
                config_path = self.user_config_path

            config = self._read_config(config_path)

            if not config.has_section(section):
                config.add_section(section)

            config.set(section, option, value)
            self._write_config(config, config_path)
            return True
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False

    def remove_config(self, section: str, option: Optional[str] = None, scope: str = "user") -> bool:
        """
        删除配置项或配置段
        
        Args:
            section: 配置段
            option: 配置项，如果为 None 则删除整个配置段
            scope: 配置级别
            
        Returns:
            是否删除成功
        """
        try:
            if scope == "user":
                config_path = self.user_config_path
            elif scope == "global":
                config_path = self.global_config_path
            elif scope == "local":
                config_path = self._get_local_config_path()
            else:
                config_path = self.user_config_path

            config = self._read_config(config_path)

            if option is None:
                # 删除整个配置段
                if config.has_section(section):
                    config.remove_section(section)
            else:
                # 删除配置项
                if config.has_section(section) and config.has_option(section, option):
                    config.remove_option(section, option)

            self._write_config(config, config_path)
            return True
        except Exception as e:
            print(f"删除配置失败: {e}")
            return False

    def get_config_path(self, scope: str = "user") -> Path:
        """
        获取配置文件路径
        
        Args:
            scope: 配置级别 ('user', 'global', 'local')
            
        Returns:
            配置文件路径
            
        Raises:
            ValueError: 如果 scope='local' 但未检测到虚拟环境
        """
        if scope == "user":
            return self.user_config_path
        elif scope == "global":
            return self.global_config_path
        elif scope == "local":
            return self._get_local_config_path()
        else:
            return self.user_config_path
    
    def is_in_virtualenv(self) -> bool:
        """
        检查是否在虚拟环境中
        
        Returns:
            是否在虚拟环境中
        """
        return os.environ.get('VIRTUAL_ENV') is not None
    
    def get_virtualenv_path(self) -> Optional[Path]:
        """
        获取当前虚拟环境路径
        
        Returns:
            虚拟环境路径，如果不在虚拟环境中则返回 None
        """
        virtual_env = os.environ.get('VIRTUAL_ENV')
        return Path(virtual_env) if virtual_env else None

