"""Python RPG 戦闘システム - メインエントリーポイント"""

import time
from rich.console import Console
from rich.panel import Panel

from battle import start_battle

console = Console()


if __name__ == "__main__":
    console.print(Panel(
        "[bold cyan]Python RPG 戦闘システム デモ[/bold cyan]\n\n[white]richライブラリを使用した\nターン制バトルシステム[/white]",
        title="🎮 ゲームスタート",
        border_style="bold cyan"
    ))
    time.sleep(2)

    start_battle()

    console.print("\n[dim]ゲームを終了します...[/dim]")
