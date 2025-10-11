"""可视化配置编辑器 - 使用 Textual 创建 TUI 界面"""

import configparser
from pathlib import Path
from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Static,
)


class AddConfigDialog(ModalScreen[tuple[str, str, str]]):
    """添加配置项的对话框"""

    CSS = """
    AddConfigDialog {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #dialog Label {
        margin-bottom: 1;
    }

    #dialog Input {
        margin-bottom: 1;
    }

    #dialog Horizontal {
        height: auto;
        margin-top: 1;
    }

    #dialog Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("添加配置项", id="title")
            yield Label("Section (配置段):")
            yield Input(placeholder="例如: global", id="section_input")
            yield Label("Option (配置项):")
            yield Input(placeholder="例如: index-url", id="option_input")
            yield Label("Value (配置值):")
            yield Input(placeholder="例如: https://pypi.org/simple", id="value_input")
            
            with Horizontal():
                yield Button("确定", variant="primary", id="confirm")
                yield Button("取消", variant="default", id="cancel")

    @on(Button.Pressed, "#confirm")
    def handle_confirm(self) -> None:
        section = self.query_one("#section_input", Input).value.strip()
        option = self.query_one("#option_input", Input).value.strip()
        value = self.query_one("#value_input", Input).value.strip()
        
        if section and option and value:
            self.dismiss((section, option, value))
        else:
            self.notify("请填写所有字段", severity="warning")

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self) -> None:
        self.dismiss(None)


class ConfigEditorApp(App[None]):
    """pip 配置文件编辑器"""

    CSS = """
    Screen {
        background: $background;
    }

    #header_info {
        dock: top;
        height: 3;
        background: $accent;
        padding: 1 2;
    }

    #main_container {
        height: 100%;
        padding: 1 2;
    }

    #config_display {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        padding: 1 2;
        overflow-y: scroll;
    }

    #button_bar {
        dock: bottom;
        height: 3;
        padding: 0 2;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "退出"),
        ("a", "add_config", "添加"),
        ("d", "delete_config", "删除"),
        ("s", "save", "保存"),
        ("r", "reload", "重新加载"),
    ]

    def __init__(self, config_path: Path, scope: str):
        super().__init__()
        self.config_path = config_path
        self.scope = scope
        self.config = configparser.ConfigParser()
        self.modified = False
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                self.config.read(self.config_path, encoding="utf-8")
            except Exception as e:
                self.notify(f"加载配置失败: {e}", severity="error")

    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                self.config.write(f)
            
            self.modified = False
            return True
        except Exception as e:
            self.notify(f"保存配置失败: {e}", severity="error")
            return False

    def compose(self) -> ComposeResult:
        """构建 UI"""
        yield Header()
        
        with Container(id="header_info"):
            yield Label(f"📝 编辑 pip 配置文件 ({self.scope})")
            yield Label(f"路径: {self.config_path}")

        with Vertical(id="main_container"):
            yield Static(id="config_display")

        with Horizontal(id="button_bar"):
            yield Button("添加 (A)", variant="primary", id="btn_add")
            yield Button("删除 (D)", variant="error", id="btn_delete")
            yield Button("保存 (S)", variant="success", id="btn_save")
            yield Button("重新加载 (R)", variant="default", id="btn_reload")
            yield Button("退出 (Q)", variant="default", id="btn_quit")

        yield Footer()

    def on_mount(self) -> None:
        """挂载时更新显示"""
        self.update_display()

    def update_display(self) -> None:
        """更新配置显示"""
        display = self.query_one("#config_display", Static)
        
        if not self.config.sections():
            display.update("[dim]配置文件为空\n按 'A' 或点击 '添加' 按钮添加配置项[/dim]")
            return

        lines = []
        for section in self.config.sections():
            lines.append(f"[bold cyan][{section}][/bold cyan]")
            
            for option, value in self.config.items(section):
                lines.append(f"  [yellow]{option}[/yellow] = [green]{value}[/green]")
            
            lines.append("")  # 空行分隔

        display.update("\n".join(lines))

    @on(Button.Pressed, "#btn_add")
    def action_add_config(self) -> None:
        """添加配置项"""
        def handle_result(result: Optional[tuple[str, str, str]]) -> None:
            if result:
                section, option, value = result
                
                if not self.config.has_section(section):
                    self.config.add_section(section)
                
                self.config.set(section, option, value)
                self.modified = True
                self.update_display()
                self.notify(f"已添加配置: [{section}] {option} = {value}", severity="information")

        self.push_screen(AddConfigDialog(), handle_result)

    @on(Button.Pressed, "#btn_delete")
    def action_delete_config(self) -> None:
        """删除配置项（简化版：删除最后一个配置项）"""
        if not self.config.sections():
            self.notify("配置文件为空，无法删除", severity="warning")
            return

        # 简化实现：删除最后一个 section 的最后一个选项
        last_section = self.config.sections()[-1]
        options = list(self.config.options(last_section))
        
        if options:
            last_option = options[-1]
            self.config.remove_option(last_section, last_option)
            self.modified = True
            self.update_display()
            self.notify(f"已删除配置: [{last_section}] {last_option}", severity="information")
            
            # 如果 section 为空，删除 section
            if not self.config.options(last_section):
                self.config.remove_section(last_section)
        else:
            self.config.remove_section(last_section)
            self.modified = True
            self.update_display()
            self.notify(f"已删除配置段: [{last_section}]", severity="information")

    @on(Button.Pressed, "#btn_save")
    def action_save(self) -> None:
        """保存配置"""
        if self.save_config():
            self.notify("✓ 配置已保存", severity="information")
        else:
            self.notify("✗ 保存失败", severity="error")

    @on(Button.Pressed, "#btn_reload")
    def action_reload(self) -> None:
        """重新加载配置"""
        if self.modified:
            self.notify("警告: 未保存的修改将丢失", severity="warning")
        
        self.config = configparser.ConfigParser()
        self.load_config()
        self.modified = False
        self.update_display()
        self.notify("已重新加载配置", severity="information")

    @on(Button.Pressed, "#btn_quit")
    def action_quit(self) -> None:
        """退出编辑器"""
        if self.modified:
            self.notify("警告: 有未保存的修改！按 'S' 保存或再次按 'Q' 退出", severity="warning")
        else:
            self.exit()


def run_editor(config_path: Path, scope: str = "user") -> None:
    """
    运行配置编辑器
    
    Args:
        config_path: 配置文件路径
        scope: 配置级别
    """
    app = ConfigEditorApp(config_path, scope)
    app.run()


if __name__ == "__main__":
    # 测试代码
    from pathlib import Path
    test_path = Path.home() / ".pip" / "pip.conf"
    run_editor(test_path, "user")

