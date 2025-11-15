from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def show_battle_screen(player_hp, enemy_hp):
    console.clear()
    
    # タイトル
    console.print(Panel("[bold red]⚔️ 戦闘中 ⚔️[/bold red]", style="bold"))
    
    # ステータステーブル
    table = Table(show_header=False, box=None)
    table.add_row("勇者", f"[green]HP: {player_hp}/100[/green]")
    table.add_row("ゴブリン", f"[red]HP: {enemy_hp}/50[/red]")
    console.print(table)
    
    console.print()
    
    # 行動選択
    action = Prompt.ask(
        "[yellow]行動を選択[/yellow]",
        choices=["attack", "magic", "item", "run"]
    )
    
    return action