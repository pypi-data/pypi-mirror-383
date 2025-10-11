# pyrm - Python pip 镜像源管理工具

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`pyrm` (Python Registry Manager) 是一个命令行工具，用于管理 Python pip 的镜像源配置，类似于 Node.js 的 `nrm`。

## ✨ 特性

- 🚀 快速切换 pip 镜像源
- 📊 测试镜像源速度
- 🎨 美观的命令行界面（基于 Rich）
- 📝 可视化编辑 pip 配置文件（基于 Textual）
- 🔧 支持自定义镜像源
- 📦 支持项目级镜像源配置
- 🌍 内置国内常用镜像源

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
pip install py-mirror-cli
```

安装完成后，使用 `pyrm` 命令即可。

### 从源码安装（开发环境）

```bash
# 克隆仓库
git clone https://github.com/yourusername/py-mirror-cli.git
cd py-mirror-cli

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

### 从 PyPI 安装

```bash
pip install py-mirror-cli
```

安装完成后，使用 `pyrm` 命令即可。

## 🚀 快速开始

### 列出所有可用的镜像源

```bash
pyrm ls

# 或测试所有镜像源速度
pyrm ls --test
```

### 切换镜像源

```bash
# 切换到清华源
pyrm use tsinghua

# 切换到阿里云
pyrm use aliyun

# 切换全局镜像源（需要管理员权限）
pyrm use tsinghua --scope global

# 为当前项目设置镜像源
pyrm use tsinghua --scope local
```

### 查看当前使用的镜像源

```bash
pyrm current

# 查看项目级镜像源
pyrm current --scope local
```

### 测试镜像源速度

```bash
pyrm test

# 自定义超时时间
pyrm test --timeout 10
```

### 添加自定义镜像源

```bash
pyrm add myregistry https://my-registry.com/simple --desc "我的自定义镜像源"
```

### 删除自定义镜像源

```bash
# 交互式删除
pyrm del myregistry

# 强制删除（不需要确认）
pyrm del myregistry --force
```

### 虚拟环境级镜像源

```bash
# 先激活虚拟环境
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 为当前虚拟环境设置镜像源
pyrm local tsinghua

# 查看当前虚拟环境的镜像源
pyrm local
```

**注意：** `local` 命令需要在激活的虚拟环境中使用。pip 只支持虚拟环境级别的配置，不支持项目目录下的配置文件。

### 可视化编辑配置文件

```bash
# 编辑用户级配置
pyrm edit

# 编辑项目级配置
pyrm edit --scope local

# 编辑全局配置
pyrm edit --scope global
```

## 🎯 配置级别说明

pyrm 支持三个配置级别（优先级从高到低）：

1. **local（虚拟环境级）** - 仅影响当前虚拟环境，需要先激活虚拟环境
2. **user（用户级）** - 影响当前用户的所有项目（默认）
3. **global（全局）** - 影响系统所有用户（需要管理员权限）

**重要：** `local` 级别实际上是虚拟环境级别，配置文件位于 `$VIRTUAL_ENV/pip.conf`（或 Windows 的 `pip.ini`）。pip 不支持项目目录下的配置文件。

## 📋 内置镜像源

| 名称 | URL | 说明 |
|------|-----|------|
| pypi | https://pypi.org/simple | Python 官方镜像源 |
| tsinghua | https://pypi.tuna.tsinghua.edu.cn/simple | 清华大学镜像源 |
| aliyun | https://mirrors.aliyun.com/pypi/simple | 阿里云镜像源 |
| tencent | https://mirrors.cloud.tencent.com/pypi/simple | 腾讯云镜像源 |
| douban | https://pypi.douban.com/simple | 豆瓣镜像源 |
| ustc | https://pypi.mirrors.ustc.edu.cn/simple | 中国科学技术大学镜像源 |
| huawei | https://repo.huaweicloud.com/repository/pypi/simple | 华为云镜像源 |

## 📖 命令详解

### `pyrm ls` - 列出镜像源

列出所有可用的镜像源，当前使用的镜像源会用 `*` 标记。

**选项：**
- `--test, -t`: 测试所有镜像源的速度

### `pyrm use <name>` - 切换镜像源

切换到指定的镜像源。

**参数：**
- `name`: 镜像源名称

**选项：**
- `--scope, -s`: 配置级别，可选 `user`（用户级，默认）、`global`（全局）、`local`（项目级）

### `pyrm current` - 显示当前镜像源

显示当前使用的镜像源信息。

**选项：**
- `--scope, -s`: 配置级别

### `pyrm test` - 测试镜像源速度

测试所有镜像源的响应速度，并按速度排序。

**选项：**
- `--timeout, -t`: 超时时间（秒），默认 5 秒

### `pyrm add <name> <url>` - 添加镜像源

添加自定义镜像源。

**参数：**
- `name`: 镜像源名称
- `url`: 镜像源 URL

**选项：**
- `--home`: 主页 URL
- `--desc, -d`: 描述信息

### `pyrm del <name>` - 删除镜像源

删除自定义镜像源（不能删除内置镜像源）。

**参数：**
- `name`: 镜像源名称

**选项：**
- `--force, -f`: 强制删除，不需要确认

### `pyrm local [name]` - 虚拟环境级镜像源

为当前虚拟环境设置或查看镜像源。

**参数：**
- `name`: 镜像源名称（可选，留空则显示当前虚拟环境镜像源）

**注意：** 此命令需要在激活的虚拟环境中使用。pip 只支持虚拟环境级别的配置，不支持项目目录下的配置文件。

**示例：**
```bash
# 先激活虚拟环境
source venv/bin/activate

# 为虚拟环境设置镜像源
pyrm local tsinghua

# 查看虚拟环境的镜像源
pyrm local
```

### `pyrm edit` - 可视化编辑配置

打开可视化编辑器编辑 pip 配置文件。

**选项：**
- `--scope, -s`: 配置级别

**编辑器快捷键：**
- `A`: 添加配置项
- `D`: 删除配置项
- `S`: 保存配置
- `R`: 重新加载配置
- `Q`: 退出编辑器

### `pyrm version` - 显示版本

显示 pyrm 的版本信息。

## 🔧 配置文件位置

### Linux/macOS

- 用户级: `~/.pip/pip.conf` 或 `~/.config/pip/pip.conf`
- 全局: `/etc/pip.conf` 或 `/Library/Application Support/pip/pip.conf`
- 虚拟环境级: `$VIRTUAL_ENV/pip.conf`

### Windows

- 用户级: `%USERPROFILE%\pip\pip.ini`
- 全局: `C:\ProgramData\pip\pip.ini`
- 虚拟环境级: `%VIRTUAL_ENV%\pip.ini`

## 💡 使用场景

### 场景 1: 快速切换到国内镜像源

在国内使用官方源速度较慢，可以快速切换到清华源：

```bash
pyrm use tsinghua
```

### 场景 2: 不同虚拟环境使用不同镜像源

某些项目需要使用特定镜像源，可以在虚拟环境中单独配置：

```bash
# 项目 A
cd project-a
python -m venv venv
source venv/bin/activate
pyrm local tsinghua

# 项目 B
cd ../project-b
python -m venv venv
source venv/bin/activate
pyrm local aliyun
```

### 场景 3: 找到最快的镜像源

测试所有镜像源的速度，选择最快的：

```bash
pyrm test
# 查看测试结果，选择最快的镜像源
pyrm use <fastest-registry>
```

### 场景 4: 添加公司内部镜像源

```bash
pyrm add company https://pypi.company.com/simple --desc "公司内部镜像源"
pyrm use company
```

## 🛠️ 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black pyrm/
isort pyrm/
```

### 代码检查

```bash
flake8 pyrm/
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

[MIT License](LICENSE)

## 🙏 致谢

- 灵感来源于 Node.js 的 [nrm](https://github.com/Pana/nrm)
- 使用 [Typer](https://typer.tiangolo.com/) 构建 CLI
- 使用 [Rich](https://rich.readthedocs.io/) 美化终端输出
- 使用 [Textual](https://textual.textualize.io/) 构建 TUI 编辑器

## 📮 反馈

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/yourusername/py-mirror-cli/issues)
- 发送邮件至 jonelee@example.com

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！

