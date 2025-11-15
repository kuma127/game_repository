from rich.panel import Panel
from rich.console import Console

console = Console()

# イベントやメッセージを枠で囲む
console.print(Panel(
    "古びた宝箱を見つけた!\n[yellow]開けますか?[/yellow]",
    title="発見",
    border_style="green"
))