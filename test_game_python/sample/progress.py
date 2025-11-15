from rich.progress import track
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
import time

console = Console()

# 戦闘アニメーション
for i in track(range(100), description="攻撃中..."):
    time.sleep(0.01)

# HPバー
with Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(bar_width=20),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:
    hp_task = progress.add_task("[red]HP", total=100, completed=75)
