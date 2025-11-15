from rich.live import Live
from rich.table import Table
import time

def generate_status_table(hp, mp):
    table = Table()
    table.add_column("ステータス")
    table.add_column("値")
    table.add_row("HP", f"[red]{hp}/100[/red]")
    table.add_row("MP", f"[blue]{mp}/50[/blue]")
    return table

# リアルタイムで更新される表示
with Live(generate_status_table(100, 50), refresh_per_second=4) as live:
    hp = 100
    for _ in range(10):
        time.sleep(0.5)
        hp -= 10
        live.update(generate_status_table(hp, 50))