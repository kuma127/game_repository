from rich.console import Console

console = Console()

# 色付きテキスト
console.print("[bold red]敵が現れた![/bold red]")
console.print("[green]HP: 100/100[/green]")

# スタイル付きテキスト
console.print("ゴブリンの攻撃!", style="bold yellow")