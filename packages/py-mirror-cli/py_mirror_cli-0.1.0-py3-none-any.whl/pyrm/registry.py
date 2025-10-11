"""镜像源管理模块"""

import json
from pathlib import Path
from typing import Dict, Optional

# 内置的镜像源
BUILTIN_REGISTRIES = {
    "pypi": {
        "name": "pypi",
        "url": "https://pypi.org/simple",
        "home": "https://pypi.org",
        "description": "Python 官方镜像源",
    },
    "tsinghua": {
        "name": "tsinghua",
        "url": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "home": "https://mirrors.tuna.tsinghua.edu.cn/help/pypi/",
        "description": "清华大学镜像源",
    },
    "aliyun": {
        "name": "aliyun",
        "url": "https://mirrors.aliyun.com/pypi/simple",
        "home": "https://mirrors.aliyun.com/pypi/",
        "description": "阿里云镜像源",
    },
    "tencent": {
        "name": "tencent",
        "url": "https://mirrors.cloud.tencent.com/pypi/simple",
        "home": "https://mirrors.cloud.tencent.com/pypi/",
        "description": "腾讯云镜像源",
    },
    "douban": {
        "name": "douban",
        "url": "https://pypi.douban.com/simple",
        "home": "https://pypi.douban.com",
        "description": "豆瓣镜像源",
    },
    "ustc": {
        "name": "ustc",
        "url": "https://pypi.mirrors.ustc.edu.cn/simple",
        "home": "https://mirrors.ustc.edu.cn/help/pypi.html",
        "description": "中国科学技术大学镜像源",
    },
    "huawei": {
        "name": "huawei",
        "url": "https://repo.huaweicloud.com/repository/pypi/simple",
        "home": "https://mirrors.huaweicloud.com",
        "description": "华为云镜像源",
    },
}


class RegistryManager:
    """镜像源管理器"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化镜像源管理器
        
        Args:
            config_dir: 配置目录路径，默认为 ~/.pyrm
        """
        self.config_dir = config_dir or Path.home() / ".pyrm"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.custom_registry_file = self.config_dir / "registries.json"
        self._custom_registries = self._load_custom_registries()

    def _load_custom_registries(self) -> Dict:
        """加载自定义镜像源"""
        if self.custom_registry_file.exists():
            try:
                with open(self.custom_registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_custom_registries(self) -> None:
        """保存自定义镜像源"""
        with open(self.custom_registry_file, "w", encoding="utf-8") as f:
            json.dump(self._custom_registries, f, indent=2, ensure_ascii=False)

    def get_all_registries(self) -> Dict:
        """获取所有镜像源（内置 + 自定义）"""
        all_registries = BUILTIN_REGISTRIES.copy()
        all_registries.update(self._custom_registries)
        return all_registries

    def get_registry(self, name: str) -> Optional[Dict]:
        """
        获取指定名称的镜像源
        
        Args:
            name: 镜像源名称
            
        Returns:
            镜像源信息，如果不存在则返回 None
        """
        all_registries = self.get_all_registries()
        return all_registries.get(name)

    def add_registry(
        self, name: str, url: str, home: str = "", description: str = ""
    ) -> bool:
        """
        添加自定义镜像源
        
        Args:
            name: 镜像源名称
            url: 镜像源 URL
            home: 主页 URL
            description: 描述
            
        Returns:
            是否添加成功
        """
        if name in BUILTIN_REGISTRIES:
            return False  # 不能覆盖内置镜像源

        self._custom_registries[name] = {
            "name": name,
            "url": url,
            "home": home or url,
            "description": description or f"自定义镜像源: {name}",
        }
        self._save_custom_registries()
        return True

    def delete_registry(self, name: str) -> bool:
        """
        删除自定义镜像源
        
        Args:
            name: 镜像源名称
            
        Returns:
            是否删除成功
        """
        if name in BUILTIN_REGISTRIES:
            return False  # 不能删除内置镜像源

        if name in self._custom_registries:
            del self._custom_registries[name]
            self._save_custom_registries()
            return True
        return False

    def is_builtin(self, name: str) -> bool:
        """
        判断是否为内置镜像源
        
        Args:
            name: 镜像源名称
            
        Returns:
            是否为内置镜像源
        """
        return name in BUILTIN_REGISTRIES

