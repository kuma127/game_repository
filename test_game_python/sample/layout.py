from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

console = Console()

layout = Layout()
layout.split_column(
    Layout(name="header", size=3),
    Layout(name="body"),
    Layout(name="footer", size=3)
)

layout["header"].update(Panel("⚔️ RPGゲーム", style="bold magenta"))
layout["body"].update(Panel("ゲーム画面"))
layout["footer"].update(Panel("HP: 100 | MP: 50", style="green"))

console.print(layout)
